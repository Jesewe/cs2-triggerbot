<div align="center">
   <img src="src/img/icon.png" alt="CS2 TriggerBot" width="200" height="200">
   <h1>🎯 CS2 TriggerBot 🎯</h1>
   <p>Tu asistente definitivo de puntería para Counter-Strike 2</p>
   <a href="#características"><strong>Características</strong></a> •
   <a href="#instalación"><strong>Instalación</strong></a> •
   <a href="#uso"><strong>Uso</strong></a> •
   <a href="#personalización"><strong>Personalización</strong></a> •
   <a href="#solución-de-problemas"><strong>Solución de problemas</strong></a> •
   <a href="#contribución"><strong>Contribución</strong></a>
   <br><br>
   <p><strong>🌍 Traducciones:</strong></p>
   <a href="README.ru.md"><img src="https://img.shields.io/badge/lang-Russian-purple?style=for-the-badge&logo=googletranslate"></a>
   <a href="README.fr.md"><img src="https://img.shields.io/badge/lang-French-purple?style=for-the-badge&logo=googletranslate"></a>
   <a href="README.es.md"><img src="https://img.shields.io/badge/lang-Spanish-purple?style=for-the-badge&logo=googletranslate"></a>
   <a href="README.uk-UA.md"><img src="https://img.shields.io/badge/lang-Ukrainian-purple?style=for-the-badge&logo=googletranslate"></a>
   <a href="README.pl.md"><img src="https://img.shields.io/badge/lang-Polish-purple?style=for-the-badge&logo=googletranslate"></a>
</div>

---

# Descripción general
CS2 TriggerBot es una herramienta automatizada diseñada para Counter-Strike 2 que ayuda con la puntería precisa al activar automáticamente un clic del ratón cuando se detecta un enemigo en la mira del jugador.

## Características
- **Disparo automático:** Activa automáticamente un clic del ratón cuando se detecta un enemigo.
- **Conexión al proceso:** Se conecta al proceso `cs2.exe` y lee los valores de memoria para tomar decisiones en tiempo real.
- **Tecla de activación personalizable:** Permite a los usuarios definir su propia tecla de activación.
- **Comprobación de actualizaciones:** Verifica automáticamente la última versión y notifica al usuario si hay una actualización disponible.
- **Registro de errores:** Guarda errores y eventos importantes en un archivo de registro para fines de depuración.

## Instalación
1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Jesewe/cs2-triggerbot.git
   cd cs2-triggerbot
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar el script:**
   ```bash
   python main.py
   ```

## Uso
1. Asegúrate de que Counter-Strike 2 esté en ejecución.
2. Ejecuta el script utilizando el comando anterior.
3. El script comprobará automáticamente si hay actualizaciones y obtendrá los offsets necesarios de las fuentes proporcionadas.
4. Una vez que el script esté en funcionamiento, presiona la tecla de activación configurada (por defecto: `X`) para activar TriggerBot.
5. La herramienta simulará automáticamente clics del ratón cuando se detecte un enemigo en la mira.

## Personalización
- **Tecla de activación:** Puedes cambiar la tecla de activación modificando la variable `TRIGGER_KEY` en el script.
- **Directorio de registros:** Los archivos de registro se guardan por defecto en el directorio `%LOCALAPPDATA%\Requests\ItsJesewe\crashes`. Puedes cambiar esto modificando la variable `LOG_DIRECTORY`.

## Solución de problemas
- **Error al obtener offsets:** Asegúrate de que tienes una conexión a Internet activa y que las URL de origen son accesibles.
- **No se pudo abrir `cs2.exe`:** Asegúrate de que el juego esté en ejecución y que tienes los permisos necesarios.
- **Errores inesperados:** Consulta el archivo de registro ubicado en el directorio de registros para obtener más detalles.

## Contribución
¡Las contribuciones son bienvenidas! Por favor, abre un issue o envía un pull request en el [repositorio de GitHub](https://github.com/Jesewe/cs2-triggerbot).

## Descargo de responsabilidad
Este script es solo para fines educativos. El uso de trampas o hacks en juegos en línea está en contra de los términos de servicio de la mayoría de los juegos y puede resultar en prohibiciones u otras sanciones. Usa este script bajo tu propio riesgo.

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.