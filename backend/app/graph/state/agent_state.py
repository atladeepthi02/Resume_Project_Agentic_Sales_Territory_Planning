from backend.app.graph.state.account_state import AccountState
from backend.app.graph.state.territory_state import TerritoryState
from backend.app.graph.state.workflow_state import WorkflowState


class AgentState(WorkflowState, TerritoryState, AccountState, total=False):
    pass