def canasta_counter(request):
    """
    Context Processor para inyectar globalmente la cantidad de equipos cotizados
    en todas las plantillas del sitio (Navbar, botones, etc.).
    """
    canasta = request.session.get('canasta_arriendo', {})
    total_items = sum(item.get('dias', 1) for item in canasta.values()) if canasta else 0
    total_equipos = len(canasta)
    return {
        'canasta_total_items': total_items,
        'canasta_total_equipos': total_equipos,
    }
