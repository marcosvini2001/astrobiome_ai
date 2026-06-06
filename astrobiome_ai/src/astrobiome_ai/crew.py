from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from astrobiome_ai.tools.rag_tool import BotanyLiteratureSearchTool
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class AstrobiomeAi():
    """AstrobiomeAi crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def telemetry_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['telemetry_analyst'], # type: ignore[index]
            verbose=True
        )

    @agent
    def aerospace_botanist(self) -> Agent:
        return Agent(
            config=self.agents_config['aerospace_botanist'], # type: ignore[index]
            tools=[BotanyLiteratureSearchTool()],
            verbose=True
        )

    @agent
    def resource_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['resource_engineer'], # type: ignore[index]
            verbose=True
        )

    @agent
    def commander(self) -> Agent:
        return Agent(
            config=self.agents_config['commander'], # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def telemetry_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['telemetry_analysis_task'], # type: ignore[index]
        )

    @task
    def botanical_solution_task(self) -> Task:
        return Task(
            config=self.tasks_config['botanical_solution_task'], # type: ignore[index]
            context=[self.telemetry_analysis_task()],
        )

    @task
    def resource_impact_task(self) -> Task:
        return Task(
            config=self.tasks_config['resource_impact_task'], # type: ignore[index]
            context=[self.botanical_solution_task()],
        )

    @task
    def command_order_task(self) -> Task:
        return Task(
            config=self.tasks_config['command_order_task'], # type: ignore[index]
            context=[
                self.telemetry_analysis_task(),
                self.botanical_solution_task(),
                self.resource_impact_task(),
            ],
            output_file='command_order.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AstrobiomeAi crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
