using UnityEngine;

/// Zero-setup: press Play in ANY scene and the arm, floor, light and camera
/// are created automatically (unless a GestureRobotArm already exists).
public static class GestureArmBootstrap
{
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void Init()
    {
#if UNITY_2023_1_OR_NEWER
        if (Object.FindFirstObjectByType<GestureRobotArm>() != null) return;
#else
        if (Object.FindObjectOfType<GestureRobotArm>() != null) return;
#endif
        var floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
        floor.name = "Floor";
        floor.transform.localScale = new Vector3(0.6f, 1, 0.6f);
        floor.GetComponent<Renderer>().material.color = new Color(0.22f, 0.24f, 0.28f);

        var arm = new GameObject("GestureRobotArm");
        arm.AddComponent<GestureUdpReceiver>();
        arm.AddComponent<GestureRobotArm>();

        var cam = Camera.main;
        if (cam == null)
        {
            cam = new GameObject("Main Camera").AddComponent<Camera>();
            cam.tag = "MainCamera";
        }
        cam.transform.position = new Vector3(2.4f, 1.8f, -2.8f);
        cam.transform.LookAt(new Vector3(0, 0.9f, 0));

#if UNITY_2023_1_OR_NEWER
        if (Object.FindFirstObjectByType<Light>() == null)
#else
        if (Object.FindObjectOfType<Light>() == null)
#endif
        {
            var l = new GameObject("Sun").AddComponent<Light>();
            l.type = LightType.Directional;
            l.transform.rotation = Quaternion.Euler(50, -30, 0);
        }
    }
}
