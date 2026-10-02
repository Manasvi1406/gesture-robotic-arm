using UnityEngine;

/// Builds a simple 4-DOF arm + 2-finger gripper from primitives and drives it
/// from GestureUdpReceiver packets. No models or prefabs required.
[RequireComponent(typeof(GestureUdpReceiver))]
public class GestureRobotArm : MonoBehaviour
{
    [Header("Motion")]
    public float smoothSpeed = 12f;          // higher = snappier
    public bool invertBase, invertShoulder, invertElbow, invertWrist;

    [Header("Joint transforms (auto-built if left empty)")]
    public Transform yawPivot, shoulderPivot, elbowPivot, wristPivot, fingerLeft, fingerRight;

    GestureUdpReceiver rx;
    float base_, shoulder_, elbow_, wrist_, grip_ = 1f;
    bool hasSignal, tracking;

    const float FingerClosed = 0.012f, FingerTravel = 0.06f;

    void Start()
    {
        rx = GetComponent<GestureUdpReceiver>();
        if (yawPivot == null) Build();
    }

    void Update()
    {
        GesturePacket p = rx.Get(out double age);
        hasSignal = age < 1.0;
        tracking = hasSignal && p.tracking;

        if (hasSignal)
        {
            float k = 1f - Mathf.Exp(-smoothSpeed * Time.deltaTime);
            base_ = Mathf.Lerp(base_, p.base_yaw * (invertBase ? -1 : 1), k);
            shoulder_ = Mathf.Lerp(shoulder_, p.shoulder * (invertShoulder ? -1 : 1), k);
            elbow_ = Mathf.Lerp(elbow_, p.elbow * (invertElbow ? -1 : 1), k);
            wrist_ = Mathf.Lerp(wrist_, p.wrist * (invertWrist ? -1 : 1), k);
            grip_ = Mathf.Lerp(grip_, p.gripper, k);
        }

        // Positive pitch tilts the arm toward +X (matches the ROS 2 URDF).
        yawPivot.localRotation = Quaternion.Euler(0, base_, 0);
        shoulderPivot.localRotation = Quaternion.Euler(0, 0, -shoulder_);
        elbowPivot.localRotation = Quaternion.Euler(0, 0, -elbow_);
        wristPivot.localRotation = Quaternion.Euler(0, wrist_, 0);

        float x = FingerClosed + grip_ * FingerTravel;
        fingerLeft.localPosition = new Vector3(-x, fingerLeft.localPosition.y, 0);
        fingerRight.localPosition = new Vector3(x, fingerRight.localPosition.y, 0);
    }

    void OnGUI()
    {
        string status = !hasSignal ? "NO SIGNAL (start the Python tracker)" : tracking ? "TRACKING" : "HAND LOST";
        GUI.Label(new Rect(10, 10, 420, 24), $"Gesture Arm: {status}");
        GUI.Label(new Rect(10, 30, 420, 24),
            $"base {base_:0}  shoulder {shoulder_:0}  elbow {elbow_:0}  wrist {wrist_:0}  grip {grip_:0.00}");
    }

    // ---------------------------------------------------------------- build
    void Build()
    {
        var orange = new Color(0.95f, 0.5f, 0.1f);
        var blue = new Color(0.15f, 0.45f, 0.85f);
        var grey = new Color(0.35f, 0.35f, 0.4f);
        var green = new Color(0.2f, 0.75f, 0.4f);

        Visual(PrimitiveType.Cylinder, transform, new Vector3(0, 0.05f, 0), new Vector3(0.5f, 0.05f, 0.5f), grey);

        yawPivot = Pivot("Yaw", transform, new Vector3(0, 0.1f, 0));
        Visual(PrimitiveType.Cylinder, yawPivot, new Vector3(0, 0.1f, 0), new Vector3(0.28f, 0.1f, 0.28f), blue);

        shoulderPivot = Pivot("Shoulder", yawPivot, new Vector3(0, 0.2f, 0));
        Visual(PrimitiveType.Sphere, shoulderPivot, Vector3.zero, Vector3.one * 0.16f, grey);
        Visual(PrimitiveType.Cube, shoulderPivot, new Vector3(0, 0.4f, 0), new Vector3(0.12f, 0.8f, 0.12f), orange);

        elbowPivot = Pivot("Elbow", shoulderPivot, new Vector3(0, 0.8f, 0));
        Visual(PrimitiveType.Sphere, elbowPivot, Vector3.zero, Vector3.one * 0.14f, grey);
        Visual(PrimitiveType.Cube, elbowPivot, new Vector3(0, 0.35f, 0), new Vector3(0.1f, 0.7f, 0.1f), blue);

        wristPivot = Pivot("Wrist", elbowPivot, new Vector3(0, 0.7f, 0));
        Visual(PrimitiveType.Cube, wristPivot, new Vector3(0, 0.03f, 0), new Vector3(0.2f, 0.06f, 0.08f), grey);

        fingerLeft = Visual(PrimitiveType.Cube, wristPivot, new Vector3(-0.05f, 0.135f, 0), new Vector3(0.03f, 0.15f, 0.06f), green).transform;
        fingerRight = Visual(PrimitiveType.Cube, wristPivot, new Vector3(0.05f, 0.135f, 0), new Vector3(0.03f, 0.15f, 0.06f), green).transform;
    }

    static Transform Pivot(string name, Transform parent, Vector3 localPos)
    {
        var t = new GameObject(name).transform;
        t.SetParent(parent, false);
        t.localPosition = localPos;
        return t;
    }

    static GameObject Visual(PrimitiveType type, Transform parent, Vector3 localPos, Vector3 scale, Color color)
    {
        var go = GameObject.CreatePrimitive(type);
        Destroy(go.GetComponent<Collider>());
        go.transform.SetParent(parent, false);
        go.transform.localPosition = localPos;
        go.transform.localScale = scale;
        go.GetComponent<Renderer>().material.color = color;
        return go;
    }
}
