package com.example.tfg_jorgerey.adapter

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import androidx.core.view.isVisible
import androidx.recyclerview.widget.RecyclerView
import com.example.tfg_jorgerey.R
import com.example.tfg_jorgerey.model.Frase

/**
 * Created by pacopulido on 9/10/18.
 */
class CustomAdapter(val context: Context,
                    val layout: Int
) : RecyclerView.Adapter<CustomAdapter.ViewHolder>() {

    private var dataList: List<Frase> = emptyList()

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val layoutInflater = LayoutInflater.from(parent.context)
        val viewlayout = layoutInflater.inflate(layout, parent, false)
        return ViewHolder(viewlayout, context)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = dataList[position]
        holder.bind(item)
    }

    override fun getItemCount(): Int {
        return dataList.size
    }

    internal fun setFrases(Frases: List<Frase>) {
        this.dataList = Frases.reversed()
        notifyDataSetChanged()
    }


    class ViewHolder(viewlayout: View, val context: Context) : RecyclerView.ViewHolder(viewlayout) {
        fun bind(dataItem: Frase){
            // itemview es el item de diseño
            // al que hay que poner los datos del objeto dataIte
            val rowFrase = itemView.findViewById(R.id.botonFrase) as Button
            val rowPeticion = itemView.findViewById(R.id.botonFrase2) as Button
            if (dataItem.isRespuesta) {
                rowPeticion.isVisible = false
                rowFrase.isVisible = true
                rowFrase.text = dataItem.frase
            }else{
                rowPeticion.isVisible = true
                rowFrase.isVisible = false
                rowPeticion.text = dataItem.frase
            }
        }

    }
}