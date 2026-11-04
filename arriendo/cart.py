from decimal import Decimal
from django.conf import settings
from .models import Maquinaria

class CanastaArriendo:
    def __init__(self, request):
        self.session = request.session
        canasta = self.session.get('canasta_arriendo')
        if not canasta:
            canasta = self.session['canasta_arriendo'] = {}
        self.canasta = canasta

    def agregar(self, maquinaria, dias=1):
        maquinaria_id = str(maquinaria.id)
        if maquinaria_id not in self.canasta:
            self.canasta[maquinaria_id] = {
                'id': maquinaria.id,
                'codigo': maquinaria.codigo,
                'nombre': maquinaria.nombre,
                'marca': maquinaria.marca,
                'tarifa_diaria': float(maquinaria.tarifa_diaria),
                'garantia': float(maquinaria.garantia),
                'dias': int(dias),
                'imagen_url': maquinaria.imagen.url if maquinaria.imagen else ''
            }
        else:
            self.canasta[maquinaria_id]['dias'] = int(dias)
        self.guardar()

    def actualizar_dias(self, maquinaria_id, dias):
        m_id = str(maquinaria_id)
        if m_id in self.canasta:
            if int(dias) > 0:
                self.canasta[m_id]['dias'] = int(dias)
            else:
                self.eliminar(maquinaria_id)
            self.guardar()

    def eliminar(self, maquinaria_id):
        m_id = str(maquinaria_id)
        if m_id in self.canasta:
            del self.canasta[m_id]
            self.guardar()

    def vaciar(self):
        self.session['canasta_arriendo'] = {}
        self.guardar()

    def guardar(self):
        self.session.modified = True

    def obtener_resumen(self):
        items = []
        subtotal_neto = Decimal('0')
        total_garantias = Decimal('0')

        for item in self.canasta.values():
            tarifa = Decimal(str(item['tarifa_diaria']))
            garantia = Decimal(str(item['garantia']))
            dias = int(item['dias'])
            costo_arriendo = tarifa * dias

            subtotal_neto += costo_arriendo
            total_garantias += garantia

            items.append({
                'id': item['id'],
                'codigo': item['codigo'],
                'nombre': item['nombre'],
                'marca': item['marca'],
                'tarifa_diaria': tarifa,
                'garantia': garantia,
                'dias': dias,
                'costo_arriendo': costo_arriendo,
                'imagen_url': item.get('imagen_url', ''),
            })

        iva_19 = subtotal_neto * Decimal('0.19')
        total_final = subtotal_neto + iva_19 + total_garantias

        return {
            'items': items,
            'subtotal_neto': int(round(subtotal_neto)),
            'iva_19': int(round(iva_19)),
            'total_garantias': int(round(total_garantias)),
            'total_final': int(round(total_final)),
            'cantidad_equipos': len(items)
        }

