class GraphBuilder:

    def __init__(self):
        self.tools={

        }

        self.system_prompt= SYSTEM_PROMPT

    def tools(self):
        pass

    def agent_function(self):
        """Main agent Function"""
        user_question=state["messages"]
        input_question=[self.system_prompt] + user_question
        response=self.llm_with_tools.invoke(input_question)
        return {"messages":[response]}

    
    def builder_graph(self):
        graph_builder = StateGraph(MessegesState)
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_edge("tools", ToolNode(tools=self.tools))
        graph_builder.add_edge(START,"agent")
        graph_builder.add_conditional_edge("agent", tools_condition)
        graph_builder.add_edge("tools","agent")
        graph_builder.add_edge("agent", END)
        return graph_builder

        self.graph=graph_builder.compile()
        return self.graph
    
    def __call__(self):
        return self.builder_graph()