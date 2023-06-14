package com.example.tfg_jorgerey.model

import android.util.Log
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.PrintWriter
import java.net.Socket

class Cliente {
    fun startClient(mensaje: String?): String //Método para iniciar el cliente
    {
        val socket = Socket("192.168.126.128", 1234)
        val writer = PrintWriter(socket.getOutputStream(), true)
        Log.d("Cliente","Mando mensaje: "+mensaje)
        val reader = BufferedReader(InputStreamReader(socket.getInputStream()))

        writer.println(mensaje)

        var respuesta = reader.readLines().toString()

        writer.close()
        reader.close()
        socket.close()
        respuesta = respuesta.substring(2,respuesta.length-1)
        Log.d("Cliente","Recibo mensaje: "+ respuesta)
        return respuesta
    }

}