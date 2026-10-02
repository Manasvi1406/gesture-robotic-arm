using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

[Serializable]
public class GesturePacket
{
    public float base_yaw;   // degrees
    public float shoulder;   // degrees
    public float elbow;      // degrees
    public float wrist;      // degrees
    public float gripper;    // 0 closed .. 1 open
    public bool tracking;
}

/// Listens for JSON packets from the Python gesture tracker (or the ROS 2 node).
public class GestureUdpReceiver : MonoBehaviour
{
    public int port = 5005;

    Thread thread;
    UdpClient client;
    volatile bool running;
    readonly object gate = new object();
    GesturePacket latest = new GesturePacket { gripper = 1f };
    long lastTicks;

    void OnEnable()
    {
        running = true;
        thread = new Thread(Listen) { IsBackground = true };
        thread.Start();
    }

    void Listen()
    {
        try { client = new UdpClient(port); }
        catch (Exception e) { Debug.LogError($"UDP bind failed on port {port}: {e.Message}"); return; }

        var ep = new IPEndPoint(IPAddress.Any, 0);
        while (running)
        {
            try
            {
                byte[] data = client.Receive(ref ep);
                var p = JsonUtility.FromJson<GesturePacket>(Encoding.UTF8.GetString(data));
                if (p == null) continue;
                lock (gate) { latest = p; lastTicks = DateTime.UtcNow.Ticks; }
            }
            catch (SocketException) { if (!running) break; }
            catch (ObjectDisposedException) { break; }
            catch (Exception e) { Debug.LogWarning("Bad packet: " + e.Message); }
        }
    }

    /// Returns the latest packet and how many seconds ago it arrived (999 if never).
    public GesturePacket Get(out double ageSeconds)
    {
        lock (gate)
        {
            ageSeconds = lastTicks == 0 ? 999 : (DateTime.UtcNow.Ticks - lastTicks) / (double)TimeSpan.TicksPerSecond;
            return latest;
        }
    }

    void OnDisable()
    {
        running = false;
        client?.Close();
        thread?.Join(200);
    }
}
