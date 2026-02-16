"""LangGraph agent workflow — ReAct loop with tool calling."""

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage

from prompts.prompt import SYSTEM_PROMPT
from utils.model_loader import ModelLoader

# Import tool lists from each tool module
from tools.weather_search import weather_tools
from tools.place_search import place_tools
from tools.currency_converter import currency_tools
from tools.expense_calculator import expense_tools


class GraphBuilder:
    """
    Builds a LangGraph ReAct agent with travel-planning tools.

    Usage:
        builder = GraphBuilder(model_provider="google")
        graph = builder()          # returns a compiled StateGraph
        result = graph.invoke({"messages": ["Plan a 3-day trip to Goa"]})
    """

    def __init__(self, model_provider: str = "google"):
        self.model_loader = ModelLoader()

        # Select model based on provider
        if model_provider == "groq":
            self.llm = self.model_loader.load_groq_model()
        else:
            self.llm = self.model_loader.load_google_model()

        # Collect all tools into a single flat list
        self.tool_list = []
        self.tool_list.extend(weather_tools)
        self.tool_list.extend(place_tools)
        self.tool_list.extend(currency_tools)
        self.tool_list.extend(expense_tools)

        # Bind tools to the LLM
        self.llm_with_tools = self.llm.bind_tools(self.tool_list)
        self.system_prompt = SYSTEM_PROMPT

    # ── Agent node ──────────────────────────────────────────────
    def agent_function(self, state: MessagesState):
        """The main agent node — prepends the system prompt and calls the LLM."""
        user_messages = state["messages"]
        input_messages = [self.system_prompt] + user_messages
        response = self.llm_with_tools.invoke(input_messages)
        return {"messages": [response]}

    # ── Graph builder ───────────────────────────────────────────
    def build_graph(self):
        """Constructs and compiles the LangGraph state graph."""
        graph_builder = StateGraph(MessagesState)

        # Add nodes
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tool_list))

        # Add edges
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", tools_condition)
        graph_builder.add_edge("tools", "agent")

        # Compile and return
        compiled_graph = graph_builder.compile()
        return compiled_graph

    def __call__(self):
        return self.build_graph()