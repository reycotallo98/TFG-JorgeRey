package com.example.tfg_jorgerey.view


import android.content.Context
import android.content.SharedPreferences
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.EditText
import android.widget.ImageButton
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.tfg_jorgerey.R
import com.example.tfg_jorgerey.adapter.CustomAdapter
import com.example.tfg_jorgerey.databinding.ActivityMainBinding
import com.example.tfg_jorgerey.model.Cliente
import com.example.tfg_jorgerey.model.Frase
import com.google.gson.Gson
import kotlinx.coroutines.DelicateCoroutinesApi
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext


class MainActivity : AppCompatActivity() {
    private lateinit var adapter: CustomAdapter
    private lateinit var rvfrases: RecyclerView
    private lateinit var conversacion: java.util.ArrayList<Frase>
    private lateinit var conversacionSH: SharedPreferences
    private lateinit var contadorSH: SharedPreferences
    private lateinit var user:SharedPreferences
    private lateinit var binding: ActivityMainBinding
    private lateinit var tex: EditText
    private lateinit var boton: ImageButton
    var cliente = Cliente()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        user = getSharedPreferences("usuario", Context.MODE_PRIVATE)
        val usuario = ArrayList<String>()
        for ((key, value) in user.all) {
            val usurio = value.toString()

            usuario.add(usurio)
        }
        if (usuario.size == 0) {

        }
            binding = ActivityMainBinding.inflate(layoutInflater)
            setContentView(binding.root)

            conversacionSH = getSharedPreferences("frases", Context.MODE_PRIVATE)
            contadorSH = getSharedPreferences("contador", Context.MODE_PRIVATE)

            initContador()
            initRV()
            getFrases()
            showFrases()
            boton = binding.cm.button
            tex = binding.cm.editTextText

            boton.setOnClickListener(View.OnClickListener() {
                save(tex.text.toString())
                tex.text.clear()
            });

            rvfrases = binding.cm.recyclerView
            rvfrases.getLayoutManager()?.scrollToPosition(conversacion.size - 1);

    }

    companion object {
        private const val REQUEST_CODE_STT = 1
    }

    fun initContador() {
        val c = contadorSH.getInt("c", -1)
        if (c == -1) {
            val editor = contadorSH.edit()
            editor.putInt("c", 0)
            editor.apply()
        }
    }

    fun showFrases() {
        adapter.setFrases(conversacion)
    }

    fun getFrases() {
        val fraseAll = conversacionSH.all
        conversacion = ArrayList<Frase>()
        for ((key, value) in fraseAll) {
            val fraseJson = value.toString()
            val frase = Gson().fromJson(fraseJson, Frase::class.java)
            conversacion.add(frase)
        }
    }

    fun incContador(c: Int) {
        val editor = contadorSH.edit()
        editor.putInt("c", c + 1)
        editor.apply()
    }

    fun getContador(): Int {
        val c = contadorSH.getInt("c", -1)
        incContador(c)
        return c + 1
    }


    @OptIn(DelicateCoroutinesApi::class)
    fun save(frase: String) {
        // save en Share
        val editor = conversacionSH.edit()
        val fras = Frase(getContador(), false, frase)
        editor.putString("$fras.id", Gson().toJson(fras))
        editor.apply()
        var respue = ""
        conversacion.add(0, fras)
        adapter.setFrases(conversacion)
        // add al ArrayList
        rvfrases.getLayoutManager()?.scrollToPosition(conversacion.size - 1);
        GlobalScope.launch {
            Log.d("w", "Lanzamos cliente")

            respue = cliente.startClient(frase)
            withContext(Dispatchers.Main) {
                saveR(Frase(getContador(), true, respue))
                adapter.setFrases(conversacion)
                // add al ArrayList
                rvfrases.getLayoutManager()?.scrollToPosition(conversacion.size - 1);
            }
        }


    }

    fun saveR(frase: Frase) {
        // save en Share
        val editor = conversacionSH.edit()

        editor.putString("${frase.id}", Gson().toJson(frase))
        editor.apply()
        // add al ArrayList
        conversacion.add(0, frase)
        adapter.setFrases(conversacion)
        rvfrases.getLayoutManager()?.scrollToPosition(conversacion.size - 1);
    }

    private fun initRV() {
        adapter = CustomAdapter(this, R.layout.respuesta)
        binding.cm.recyclerView.adapter = adapter
        binding.cm.recyclerView.layoutManager = LinearLayoutManager(this)
    }

}



