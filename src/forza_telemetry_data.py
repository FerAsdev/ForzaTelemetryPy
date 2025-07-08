# forza_telemetry_data.py
from dataclasses import dataclass, field, fields

@dataclass
class ForzaTelemetryData:
    # --- Sección "Sled" ---
    IsRaceOn: int = field(default=0)
    TimestampMS: int = 0
    EngineMaxRpm: float = 0.0
    EngineIdleRpm: float = 0.0
    CurrentEngineRpm: float = 0.0

    AccelerationX: float = 0.0
    AccelerationY: float = 0.0
    AccelerationZ: float = 0.0

    VelocityX: float = 0.0
    VelocityY: float = 0.0
    VelocityZ: float = 0.0

    AngularVelocityX: float = 0.0
    AngularVelocityY: float = 0.0
    AngularVelocityZ: float = 0.0

    Yaw: float = 0.0
    Pitch: float = 0.0
    Roll: float = 0.0

    NormalizedSuspensionTravelFrontLeft: float = 0.0
    NormalizedSuspensionTravelFrontRight: float = 0.0
    NormalizedSuspensionTravelRearLeft: float = 0.0
    NormalizedSuspensionTravelRearRight: float = 0.0

    TireSlipRatioFrontLeft: float = 0.0
    TireSlipRatioFrontRight: float = 0.0
    TireSlipRatioRearLeft: float = 0.0
    TireSlipRatioRearRight: float = 0.0

    WheelRotationSpeedFrontLeft: float = 0.0
    WheelRotationSpeedFrontRight: float = 0.0
    WheelRotationSpeedRearLeft: float = 0.0
    WheelRotationSpeedRearRight: float = 0.0

    WheelOnRumbleStripFrontLeft: int = 0
    WheelOnRumbleStripFrontRight: int = 0
    WheelOnRumbleStripRearLeft: int = 0
    WheelOnRumbleStripRearRight: int = 0

    WheelInPuddleDepthFrontLeft: float = 0.0
    WheelInPuddleDepthFrontRight: float = 0.0
    WheelInPuddleDepthRearLeft: float = 0.0
    WheelInPuddleDepthRearRight: float = 0.0

    SurfaceRumbleFrontLeft: float = 0.0
    SurfaceRumbleFrontRight: float = 0.0
    SurfaceRumbleRearLeft: float = 0.0
    SurfaceRumbleRearRight: float = 0.0

    TireSlipAngleFrontLeft: float = 0.0
    TireSlipAngleFrontRight: float = 0.0
    TireSlipAngleRearLeft: float = 0.0
    TireSlipAngleRearRight: float = 0.0

    TireCombinedSlipFrontLeft: float = 0.0
    TireCombinedSlipFrontRight: float = 0.0
    TireCombinedSlipRearLeft: float = 0.0
    TireCombinedSlipRearRight: float = 0.0

    SuspensionTravelMetersFrontLeft: float = 0.0
    SuspensionTravelMetersFrontRight: float = 0.0
    SuspensionTravelMetersRearLeft: float = 0.0
    SuspensionTravelMetersRearRight: float = 0.0

    CarOrdinal: int = 0
    CarClass: int = field(default=0)
    CarPerformanceIndex: int = 0
    DrivetrainType: int = field(default=0)
    NumCylinders: int = 0

    # --- Sección "Dash" ---
    PositionX: float = 0.0
    PositionY: float = 0.0
    PositionZ: float = 0.0

    Speed: float = field(default=0.0)
    Power: float = 0.0
    Torque: float = 0.0

    # Ahora se incluyen las temperaturas en Fahrenheit (original)
    TireTempFrontLeft: float = field(default=0.0)
    TireTempFrontRight: float = field(default=0.0)
    TireTempRearLeft: float = field(default=0.0)
    TireTempRearRight: float = field(default=0.0)

    Boost: float = 0.0
    Fuel: float = 0.0
    DistanceTraveled: float = 0.0
    BestLap: float = field(default=0.0)
    LastLap: float = field(default=0.0)
    CurrentLap: float = field(default=0.0)
    CurrentRaceTime: float = field(default=0.0)

    LapNumber: int = 0
    RacePosition: int = 0
    Accel: int = 0
    Brake: int = 0
    Clutch: int = 0
    HandBrake: int = 0
    Gear: int = 0
    Steer: int = 0
    NormalizedDrivingLine: int = 0
    NormalizedAIBrakeDifference: int = 0

    TireWearFrontLeft: float = 0.0
    TireWearFrontRight: float = 0.0
    TireWearRearLeft: float = 0.0
    TireWearRearRight: float = 0.0

    TrackOrdinal: int = field(default=0)
    CarName: str = field(default="")
    TrackName: str = field(default="")

    # Nuevos campos calculados (para exportar en CSV)
    TireTempFrontLeftCelsius: float = 0.0
    TireTempFrontRightCelsius: float = 0.0
    TireTempRearLeftCelsius: float = 0.0
    TireTempRearRightCelsius: float = 0.0

    SpeedKph: float = 0.0

    def convert_fahrenheit_to_celsius(self, valueF):
        return (valueF - 32) * (5.0 / 9.0)

    @classmethod
    def get_csv_header(cls):
        hdrs = []
        for f in fields(cls):
            if f.metadata.get("csv_ignore", False):
                continue
            col_name = f.metadata.get("csv_column", f.name)
            hdrs.append(col_name)
        return ",".join(hdrs)

    def to_csv_line(self):
        values = []
        for f in fields(self):
            if f.metadata.get("csv_ignore", False):
                continue
            val = getattr(self, f.name)
            values.append(str(val) if val is not None else "")
        return ",".join(values)
