import getpass
import os
from dotenv import load_dotenv
import asyncio
from mcp_use import MCPAgent, MCPClient
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

os.environ["GOOGLE_API_KEY"] = 'AIzaSyDz-WYNCd0y1Zycydm1fW9DbL66StkIx38' 


# Define the tool
@tool(description="Get the current weather in a given location")
def get_weather(location: str) -> str:
    return "It's sunny."


def nosexddd():
# Initialize the model and bind the tool
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    llm_with_tools = llm.bind_tools([get_weather])

# Invoke the model with a query that should trigger the tool
    query = "What's the weather in San Francisco?"
    ai_msg = llm_with_tools.invoke(query)

# Check the tool calls in the response
    print(ai_msg.tool_calls)

# Example tool call message would be needed here if you were actually running the tool
    from langchain_core.messages import ToolMessage

    tool_message = ToolMessage(
        content=get_weather(*ai_msg.tool_calls[0]["args"]),
        tool_call_id=ai_msg.tool_calls[0]["id"],
    )
    ai_msg = llm_with_tools.invoke([ai_msg, tool_message])  # Example of passing tool result back
    print(ai_msg)

async def mcp_whatsapp():
    load_dotenv()
    client = MCPClient.from_config_file(os.path.join("all_mcp_servers.json"))

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")


    # Create agent with memory_enabled=True
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=30,
        memory_enabled=True,  # Enable built-in conversation memory
    )

    print("\n===== Interactive MCP Chat =====")
    print("Type 'exit' or 'quit' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("==================================\n")

    try:
        # Main chat loop
        while True:
            # Get user input
            user_input = input("\nYou: ")

            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                print("Ending conversation...")
                break

            # Check for clear history command
            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("Conversation history cleared.")
                continue

            # Get response from agent
            print("\nAssistant: ", end="", flush=True)

            try:
                # Run the agent with the user input (memory handling is automatic)
                response = await agent.run(user_input)
                print(response)

            except Exception as e:
                print(f"\nError: {e}")

    finally:
        # Clean up
        if client and client.sessions:
            await client.close_all_sessions()

asyncio.run(mcp_whatsapp())

