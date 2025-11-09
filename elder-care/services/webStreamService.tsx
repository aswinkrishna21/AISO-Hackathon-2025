/**
 * Streaming networking helpers.
 *
 * - `streamRequest` performs an HTTP request and yields chunks from the response body as they arrive.
 * - It supports NDJSON (newline-delimited JSON) by parsing each line as JSON when requested.
 * - If streaming isn't available in the environment, it falls back to returning the full body once.
 *
 * The implementation uses the WHATWG ReadableStream reader when available (web / modern RN),
 * and gracefully falls back otherwise.
 */

export type RequestOptions = {
	method?: string;
	headers?: Record<string, string>;
	/** Timeout in milliseconds. If omitted, no timeout is applied. */
	timeoutMs?: number;
	/** When true, interpret each newline-delimited chunk as JSON (NDJSON) and yield parsed objects */
	ndjson?: boolean;
};

/** A single yielded streaming item. Could be parsed JSON or a raw string chunk. */
export type StreamChunk<T = unknown> = {
	type: 'data';
	value: T | string;
} | {
	type: 'end';
};

/**
 * Perform a streaming request and yield received chunks.
 * Yields parsed JSON objects when `options.ndjson` is true and input is NDJSON.
 */
export async function* streamRequest<T = unknown>(
	url: string,
	body?: unknown,
	options: RequestOptions = {}
): AsyncGenerator<StreamChunk<T | string>, void, void> {
	const { method = body ? 'POST' : 'GET', headers = {}, timeoutMs, ndjson = false } = options;

	const controller = new AbortController();
	let timeoutId: ReturnType<typeof setTimeout> | undefined;
	if (timeoutMs && timeoutMs > 0) {
		timeoutId = setTimeout(() => controller.abort(), timeoutMs);
	}

	try {
		const fetchOptions: RequestInit = {
			method,
			headers: { ...headers },
			signal: controller.signal,
		};

		if (body != null) {
			if (!('Content-Type' in headers)) {
				(fetchOptions.headers as Record<string, string>)["Content-Type"] = 'application/json';
			}
			fetchOptions.body = typeof body === 'string' || body instanceof FormData ? (body as any) : JSON.stringify(body);
		}

		const res = await fetch(url, fetchOptions);

		// If environment provides a streaming body with getReader(), use it.
		const anyBody = (res as any).body;
		if (anyBody && typeof anyBody.getReader === 'function') {
			const reader = anyBody.getReader();
			const decoder = new TextDecoder();
			let buffer = '';

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;
				if (value) {
					buffer += decoder.decode(value, { stream: true });

					if (ndjson) {
						let newlineIndex: number;
						while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
							const line = buffer.slice(0, newlineIndex).trim();
							buffer = buffer.slice(newlineIndex + 1);
							if (!line) continue;
							try {
								const parsed = JSON.parse(line) as T;
								yield { type: 'data', value: parsed };
							} catch (_e) {
								// If JSON parse fails, yield raw line
								yield { type: 'data', value: line };
							}
						}
					} else {
						// Yield the chunk as string
						yield { type: 'data', value: buffer };
						buffer = '';
					}
				}
			}

			// flush remaining buffer
			if (buffer) {
				if (ndjson) {
					const line = buffer.trim();
					if (line) {
						try {
							const parsed = JSON.parse(line) as T;
							yield { type: 'data', value: parsed };
						} catch (_e) {
							yield { type: 'data', value: line };
						}
					}
				} else {
					yield { type: 'data', value: buffer };
				}
			}

			yield { type: 'end' };
			return;
		}

		// Fallback: no streaming reader available. Read full body once.
		const text = await res.text();
		if (ndjson) {
			const lines = text.split('\n');
			for (const raw of lines) {
				const line = raw.trim();
				if (!line) continue;
				try {
					const parsed = JSON.parse(line) as T;
					yield { type: 'data', value: parsed };
				} catch (_e) {
					yield { type: 'data', value: line };
				}
			}
		} else {
			yield { type: 'data', value: text };
		}

		yield { type: 'end' };
		return;
	} catch (err: any) {
		if (err?.name === 'AbortError') {
			// yield an end marker and return; caller can detect partial completion
			yield { type: 'end' };
			return;
		}
		// Re-throw - consumers can decide how to handle errors
		throw err;
	} finally {
		if (timeoutId) clearTimeout(timeoutId);
	}
}

/** Convenience wrapper that yields parsed JSON objects from an NDJSON stream. */
export async function* streamJson<T = unknown>(url: string, body?: unknown, options: RequestOptions = {}) {
	const it = streamRequest<T>(url, body, { ...options, ndjson: true });
	for await (const chunk of it) {
		if (chunk.type === 'data') {
			yield chunk.value as T | string;
		}
	}
}

/** Helper to collect a stream into an array (useful for tests or non-realtime consumers) */
export async function collectStream<T = unknown>(it: AsyncIterable<T | string>) {
	const out: Array<T | string> = [];
	for await (const v of it) {
		out.push(v);
	}
	return out;
}


