# telemetry_parser.py
import io
import struct
from forza_telemetry_data import ForzaTelemetryData

class TelemetryDataParser:
    FM8_PACKET_LENGTH = 331

    @staticmethod
    def parse(packet: bytes) -> ForzaTelemetryData:
        if len(packet) != TelemetryDataParser.FM8_PACKET_LENGTH:
            raise ValueError(f"Se esperaban {TelemetryDataParser.FM8_PACKET_LENGTH} bytes para FM8, pero se recibieron {len(packet)}.")

        stream = io.BytesIO(packet)
        def read(fmt: str):
            size = struct.calcsize(fmt)
            return struct.unpack(fmt, stream.read(size))[0]

        data = ForzaTelemetryData()
        # --- Sección "Sled" ---
        data.IsRaceOn = read("<i")
        data.TimestampMS = read("<I")
        data.EngineMaxRpm = read("<f")
        data.EngineIdleRpm = read("<f")
        data.CurrentEngineRpm = read("<f")

        data.AccelerationX = read("<f")
        data.AccelerationY = read("<f")
        data.AccelerationZ = read("<f")

        data.VelocityX = read("<f")
        data.VelocityY = read("<f")
        data.VelocityZ = read("<f")

        data.AngularVelocityX = read("<f")
        data.AngularVelocityY = read("<f")
        data.AngularVelocityZ = read("<f")

        data.Yaw = read("<f")
        data.Pitch = read("<f")
        data.Roll = read("<f")

        data.NormalizedSuspensionTravelFrontLeft = read("<f")
        data.NormalizedSuspensionTravelFrontRight = read("<f")
        data.NormalizedSuspensionTravelRearLeft = read("<f")
        data.NormalizedSuspensionTravelRearRight = read("<f")

        data.TireSlipRatioFrontLeft = read("<f")
        data.TireSlipRatioFrontRight = read("<f")
        data.TireSlipRatioRearLeft = read("<f")
        data.TireSlipRatioRearRight = read("<f")

        data.WheelRotationSpeedFrontLeft = read("<f")
        data.WheelRotationSpeedFrontRight = read("<f")
        data.WheelRotationSpeedRearLeft = read("<f")
        data.WheelRotationSpeedRearRight = read("<f")

        data.WheelOnRumbleStripFrontLeft = read("<i")
        data.WheelOnRumbleStripFrontRight = read("<i")
        data.WheelOnRumbleStripRearLeft = read("<i")
        data.WheelOnRumbleStripRearRight = read("<i")

        data.WheelInPuddleDepthFrontLeft = read("<f")
        data.WheelInPuddleDepthFrontRight = read("<f")
        data.WheelInPuddleDepthRearLeft = read("<f")
        data.WheelInPuddleDepthRearRight = read("<f")

        data.SurfaceRumbleFrontLeft = read("<f")
        data.SurfaceRumbleFrontRight = read("<f")
        data.SurfaceRumbleRearLeft = read("<f")
        data.SurfaceRumbleRearRight = read("<f")

        data.TireSlipAngleFrontLeft = read("<f")
        data.TireSlipAngleFrontRight = read("<f")
        data.TireSlipAngleRearLeft = read("<f")
        data.TireSlipAngleRearRight = read("<f")

        data.TireCombinedSlipFrontLeft = read("<f")
        data.TireCombinedSlipFrontRight = read("<f")
        data.TireCombinedSlipRearLeft = read("<f")
        data.TireCombinedSlipRearRight = read("<f")

        data.SuspensionTravelMetersFrontLeft = read("<f")
        data.SuspensionTravelMetersFrontRight = read("<f")
        data.SuspensionTravelMetersRearLeft = read("<f")
        data.SuspensionTravelMetersRearRight = read("<f")

        data.CarOrdinal = read("<i")
        data.CarClass = read("<i")
        data.CarPerformanceIndex = read("<i")
        data.DrivetrainType = read("<i")
        data.NumCylinders = read("<i")

        # --- Sección "Dash" ---
        data.PositionX = read("<f")
        data.PositionY = read("<f")
        data.PositionZ = read("<f")

        data.Speed = read("<f")
        # Calculamos SpeedKph y lo asignamos
        data.SpeedKph = data.Speed * 3.6

        data.Power = read("<f")
        data.Torque = read("<f")

        data.TireTempFrontLeft = read("<f")
        data.TireTempFrontRight = read("<f")
        data.TireTempRearLeft = read("<f")
        data.TireTempRearRight = read("<f")

        # Calculamos las temperaturas en Celsius y asignamos a los nuevos campos
        data.TireTempFrontLeftCelsius = (data.TireTempFrontLeft - 32) * (5.0 / 9.0)
        data.TireTempFrontRightCelsius = (data.TireTempFrontRight - 32) * (5.0 / 9.0)
        data.TireTempRearLeftCelsius = (data.TireTempRearLeft - 32) * (5.0 / 9.0)
        data.TireTempRearRightCelsius = (data.TireTempRearRight - 32) * (5.0 / 9.0)

        data.Boost = read("<f")
        data.Fuel = read("<f")
        data.DistanceTraveled = read("<f")
        data.BestLap = read("<f")
        data.LastLap = read("<f")
        data.CurrentLap = read("<f")
        data.CurrentRaceTime = read("<f")

        data.LapNumber = read("<H")
        data.RacePosition = read("<B")
        data.Accel = read("<B")
        data.Brake = read("<B")
        data.Clutch = read("<B")
        data.HandBrake = read("<B")
        data.Gear = read("<B")
        data.Steer = read("<b")
        data.NormalizedDrivingLine = read("<b")
        data.NormalizedAIBrakeDifference = read("<b")

        data.TireWearFrontLeft = read("<f")
        data.TireWearFrontRight = read("<f")
        data.TireWearRearLeft = read("<f")
        data.TireWearRearRight = read("<f")

        data.TrackOrdinal = read("<i")

        return data
