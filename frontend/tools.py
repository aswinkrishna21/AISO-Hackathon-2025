from pipecat.adapters.schemas.tools_schema import ToolsSchema

tools = ToolsSchema(
    standard_tools=[
        # reset_charge_point_schema,
        # change_availability_schema,
        # change_configuration_schema,
        # set_power_limit_schema,
        # remote_start_transaction_schema,
        # remote_stop_transaction_schema,
        # unlock_connector_schema,
        # send_local_list_schema,
        # trigger_demo_scenario_schema,
        # list_demo_scenarios_schema,
        # clear_demo_scenarios_schema,
        # get_status_schema,
        # get_scenario_progress_schema,
        # get_resolution_steps_schema,
    ]
)


def get_tools() -> ToolsSchema:
    return tools