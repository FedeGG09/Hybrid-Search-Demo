"""Documentos de ejemplo para una demo de Hybrid Search en soporte técnico."""
DOCUMENTS = [
    {
        "id": "vpn_corporativa",
        "title": "VPN corporativa: conexión y resolución de problemas",
        "content": """
# VPN corporativa

## Objetivo
La VPN corporativa permite acceder a recursos internos desde fuera de la oficina. Es obligatoria para consultar carpetas compartidas, sistemas ERP y bases de datos internas.

## Síntomas frecuentes
- El usuario ingresa credenciales correctas pero la conexión falla.
- La aplicación queda en "Connecting" durante varios minutos.
- Aparece el mensaje: "No se puede establecer el túnel seguro".

## Causas típicas
1. Fecha y hora desincronizadas en el equipo.
2. Perfil de VPN corrupto o desactualizado.
3. Certificado vencido.
4. Bloqueo del puerto por parte de la red doméstica.

## Procedimiento recomendado
1. Verificar que fecha, hora y zona horaria sean correctas.
2. Reiniciar el cliente de VPN.
3. Confirmar que el usuario tenga el perfil asignado.
4. Renovar certificados si corresponde.
5. Probar desde otra red o compartir internet del teléfono.

## Escalamiento
Si después de 3 intentos la VPN sigue sin conectar, abrir ticket al equipo de infraestructura indicando usuario, horario, mensaje de error y captura de pantalla.
"""
    },
    {
        "id": "password",
        "title": "Cambio de contraseña y acceso a aplicaciones",
        "content": """
# Cambio de contraseña

## Política
La contraseña debe tener al menos 12 caracteres, incluir mayúsculas, minúsculas, números y un símbolo especial.

## Proceso
El usuario debe ingresar al portal de autoservicio, validar su identidad con MFA y definir una nueva contraseña.

## Errores comunes
- La contraseña nueva es demasiado similar a la anterior.
- El usuario no completa la validación MFA.
- El navegador tiene caché antigua y muestra una sesión vencida.

## Recomendación
Limpiar caché, cerrar sesiones activas y reintentar el proceso desde una ventana privada.

## Recuperación de acceso
Si el usuario bloqueó su cuenta, el administrador puede desbloquearla desde el panel de identidad.
"""
    },
    {
        "id": "impresoras",
        "title": "Impresoras corporativas: atascos, drivers y cola de impresión",
        "content": """
# Impresoras corporativas

## Problema
Los usuarios reportan que la impresora no responde, imprime páginas en blanco o queda con trabajos en cola.

## Diagnóstico
- Revisar si la impresora está encendida y conectada a la red.
- Verificar el estado de la cola de impresión.
- Confirmar que el driver instalado sea el correcto.
- Probar impresión de página de prueba.

## Resolución
1. Reiniciar el servicio de cola de impresión.
2. Vaciar trabajos pendientes.
3. Reinstalar el driver oficial.
4. Validar IP y conectividad.
5. Cambiar el equipo a una impresora alternativa si el dispositivo está fallando.

## Nota
Los atascos de papel requieren revisión física del equipo y no se resuelven solo por software.
"""
    },
    {
        "id": "backup",
        "title": "Backups, restauración y retención de información",
        "content": """
# Backups

## Objetivo
Garantizar disponibilidad y recuperación ante incidentes, fallas humanas o borrado accidental.

## Tipos de backup
- Completo
- Incremental
- Diferencial

## Restauración
La restauración debe solicitarse indicando sistema afectado, fecha aproximada de pérdida y nivel de prioridad.

## Consideraciones
- No se restauran datos sin autorización formal.
- La retención estándar es de 30 días.
- Los backups críticos se monitorean diariamente.

## Riesgos
Una política de retención insuficiente puede impedir recuperar información histórica necesaria para auditorías.
"""
    },
    {
        "id": "facturacion",
        "title": "Facturación y contratos de licencias empresariales",
        "content": """
# Facturación

## Alcance
Consultas sobre facturas, contratos, renovaciones y licencias de software.

## Casos frecuentes
- Factura emitida con datos fiscales incorrectos.
- Renovación de licencias pendiente.
- Diferencias entre contrato y cantidad de usuarios activos.

## Procedimiento
1. Verificar número de contrato.
2. Confirmar período facturado.
3. Revisar estado de aprobación interna.
4. Escalar al área financiera si existe discrepancia documental.

## Términos sensibles
Las solicitudes con números de contrato, CUIT o fechas exactas deben recuperarse con alta precisión.
"""
    },
]
