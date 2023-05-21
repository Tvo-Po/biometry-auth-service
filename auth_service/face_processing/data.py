from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class IdetifiedEmotions:
    angry: float
    disgust: float
    fear: float
    happy: float
    sad: float
    surprise: float
    neutral: float


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfilingRecommendation:
    is_auth_recommended: bool
    identified_emotions: IdetifiedEmotions


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthenticationResult:
    is_authenticated: bool
    recommendation: ProfilingRecommendation | None = None
