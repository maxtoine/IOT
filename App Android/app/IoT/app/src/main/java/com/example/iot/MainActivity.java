package com.example.iot;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.text.Html;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.ToggleButton;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

import org.json.JSONException;
import org.json.JSONObject;

public class MainActivity extends AppCompatActivity {

    private EditText editIP;
    private EditText editPort;
    private EditText messageBox;
    private Button btnRst;
    private Button sendButton;
    private ToggleButton btnPlayer;

    private SensorEventListener listener;

    private String status;
    private String error;
    private String temperature;
    private String humidity;
    private String light;
    private String pressure;
    private String uv;

    private Integer address1;
    private Integer address2;
    private Integer sensorId = 1;

    private TextView errorView;
    private TextView tempView;
    private TextView humView;
    private TextView lightView;
    private TextView presView;
    private TextView uvView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        startUdpReceiver();

        btnRst = findViewById(R.id.btnRst);
        btnPlayer = findViewById(R.id.btnPlayer);

        // Sends the message in the text box via UDP when the "send" button is pressed
        btnRst.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // Thread de fond pour l’envoi UDP
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        try {
                            sendUdp(null);
                        } catch (JSONException e) {
                            throw new RuntimeException(e);
                        }
                    }
                }).start();
            }
        });

        messageBox = findViewById(R.id.messageBox);
        sendButton = findViewById(R.id.sendButton);

        // Sends the content of the text box via UDP when the button is pressed
        sendButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                final String message = messageBox.getText().toString().trim();

                if (message.isEmpty()) {
                    return; // Does not send empty messages
                }

                // Thread to send the message via UDP
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        try {
                            sendUdp(message);
                        } catch (JSONException e) {
                            throw new RuntimeException(e);
                        }
                    }
                }).start();

                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        messageBox.setText("");
                    }
                });
            }
        });

        // Choose the sensor depending of the switch position
        // Able to choose between two sensors thanks to their addresses
        btnPlayer.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(btnPlayer.isChecked()){
                    sensorId = 2;
                }
                else {
                    sensorId = 1;
                }
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
    }
    @Override
    protected void onPause() {
        super.onPause();
        manager.unregisterListener(listener);
    }

    // Function that sends a JSON message via UDP
    private void sendUdp(String message) throws JSONException {

        // Gets the ip address and port for the server from the corresponding text boxes
        editIP = findViewById(R.id.editIP);
        editPort = findViewById(R.id.editPort);
        String IP = editIP.getText().toString().trim();
        String portStr = editPort.getText().toString().trim();
        int port = Integer.parseInt(portStr);

        JSONObject obj = new JSONObject();

        // Selects the sensor address
        if(sensorId == 1)
            obj.put("address", address1);
        else
            obj.put("address", address2);

        // Sends a poll request or the message if any
        if(message != null){
            obj.put("method", "message");
            obj.put("message", message);
        }
        else{
            obj.put("method", "poll");
        }

        DatagramSocket socket = null;
        try {
            socket = new DatagramSocket();
            InetAddress address = InetAddress.getByName(IP);
//            byte[] data = message.getBytes();
            byte[] data = obj.toString().getBytes();
            DatagramPacket packet =
                    new DatagramPacket(data, data.length, address, port);
            socket.send(packet);
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (socket != null && !socket.isClosed()) {
                socket.close();
            }
        }
    }

    // Thread that listens for received UDP messages
    // Parses the message in JSON
    private void startUdpReceiver() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                DatagramSocket socket = null;
                try {
                    editPort = findViewById(R.id.editPort);
                    String portStr = editPort.getText().toString().trim();
                    int port = Integer.parseInt(portStr);
                    socket = new DatagramSocket(port);
                    byte[] buffer = new byte[1024];

                    while (!Thread.currentThread().isInterrupted()) {
                        DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                        socket.receive(packet); // bloquant

                        final String received = new String(
                                packet.getData(),
                                0,
                                packet.getLength()
                        );

                        // Tries to parse message as JSON
                        try {
                            JSONObject obj = new JSONObject(received);
                            if(obj.has("status"))
                                status = obj.getString("status");
                            else
                                status = "";
                            if(status.equals("error")){
                                if(obj.has("message"))
                                    error = "From server: " + obj.getString("message");
                                else
                                    error = "There has been an error that server did not specify";
                            }
                            else if (status.equals("success")) {
                                if(obj.has("address")){
                                    // If it is the first time a message is received with address, memorize it
                                    if(sensorId == 1 && address1 == null)
                                        address1 = obj.getInt("address");
                                    else if(sensorId == 2 && address2 == null)
                                        address2 = obj.getInt("address");
                                    // Else get the values from the correct address
                                    else if((sensorId == 1 && obj.getInt("address") == address1) || (sensorId == 2 && obj.getInt("address") == address2)){
                                        error = "";
                                        if(obj.has("temperature"))
                                            temperature = obj.getString("temperature");
                                        if(obj.has("humidity"))
                                            humidity = obj.getString("humidity");
                                        if(obj.has("light"))
                                            light = obj.getString("light");
                                        if(obj.has("pressure"))
                                            pressure = obj.getString("pressure");
                                        if(obj.has("uv"))
                                            uv = obj.getString("uv");
                                    }
                                    else{
                                        // Display the address for messages from other adrresses
                                        error = "Received message from address " + obj.getInt("address");
                                    }
                                }
                            } else{
                                error = "Message status not found or not supported";
                            }

                        // Shows error if unable to parse the message as a JSON
                        } catch (Exception e) {
                            error = "Error parsing JSON";
                        }


                        // Selects the corresponding field views for displaying sensor values
                        errorView = findViewById(R.id.errorView);
                        tempView = findViewById(R.id.tempView);
                        humView = findViewById(R.id.humView);
                        lightView = findViewById(R.id.lightView);
                        presView = findViewById(R.id.presView);
                        uvView = findViewById(R.id.uvView);

                        // Displays the sensor values with field name and corresponding units
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                errorView.setText(error);
                                tempView.setText(Html.fromHtml(String.format("Temperature : <b>%s</b>°C", temperature), Html.FROM_HTML_MODE_LEGACY));
                                humView.setText(Html.fromHtml(String.format("Humidity : <b>%s</b>%%", humidity), Html.FROM_HTML_MODE_LEGACY));
                                lightView.setText(Html.fromHtml(String.format("Light : <b>%s</b> lux", light), Html.FROM_HTML_MODE_LEGACY));
                                presView.setText(Html.fromHtml(String.format("Pressure : <b>%s</b> hPa", pressure), Html.FROM_HTML_MODE_LEGACY));
                                uvView.setText(Html.fromHtml(String.format("UV : <b>%s</b>", uv), Html.FROM_HTML_MODE_LEGACY));
                            }
                        });
                    }

                } catch (Exception e) {
                    e.printStackTrace();
                } finally {
                    if (socket != null && !socket.isClosed()) {
                        socket.close();
                    }
                }
            }
        }).start();
    }
}