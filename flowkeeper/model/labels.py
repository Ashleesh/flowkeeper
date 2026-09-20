"""Focus states. Index order is the model's output order — do not reorder."""

DEEP_FOCUS = "DEEP_FOCUS"
LIGHT_WORK = "LIGHT_WORK"
IDLE = "IDLE"
AWAY = "AWAY"

STATES = [DEEP_FOCUS, LIGHT_WORK, IDLE, AWAY]

DESCRIPTIONS = {
    DEEP_FOCUS: "Steady typing in a single app, little switching — protect this.",
    LIGHT_WORK: "Reading or browsing with moderate switching.",
    IDLE: "At the machine but between tasks.",
    AWAY: "No input for a while — likely stepped away.",
}
