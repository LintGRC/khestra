from pydantic import BaseModel
from typing import Optional


class ScenarioStep(BaseModel):
    step: int
    title: str
    prompt: str
    context: str
    questions: list[str]
    expertGuidance: str
    scoringCriteria: list[str]
    frameworkRefs: list[str]
    timeAllocation: int


class Scenario(BaseModel):
    id: str
    type: str
    title: str
    description: str
    difficulty: str
    estimatedTime: str
    triggers: list[str]
    steps: list[ScenarioStep]


class ExerciseResponse(BaseModel):
    step: int
    answer: str = ""
    timeSpent: int = 0
    selfRated: int = 0


class StepScore(BaseModel):
    step: int
    title: str
    score: int
    maxScore: int
    percentage: int
    strengths: list[str]
    gaps: list[str]
    frameworkRequirements: list[str]


class Exercise(BaseModel):
    id: str
    scenarioId: str
    scenarioTitle: str
    scenarioType: str
    status: str
    participants: list[str]
    responses: list[ExerciseResponse]
    scores: list[StepScore]
    overallScore: int
    overallPercentage: int
    recommendations: list[str]
    startedAt: str
    completedAt: str = ""


class ExerciseCreateBody(BaseModel):
    scenarioId: str
    participants: list[str] = []
    responses: list[ExerciseResponse]


class ExerciseListResponse(BaseModel):
    exercises: list[Exercise]
