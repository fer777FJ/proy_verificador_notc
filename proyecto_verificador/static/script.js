let currentTab = 'texto';

function switchTab(tab) {
    currentTab = tab;

    // FIX #4: Clases correctas del dark mode para tabs inactivos
    // Las clases anteriores (text-gray-500, hover:bg-gray-100) eran del tema claro
    // y sobreescribían el diseño dark mode al cambiar de pestaña
    ['texto', 'link', 'imagen'].forEach(t => {
        document.getElementById(`sec-${t}`).classList.add('hidden');
        document.getElementById(`tab-${t}`).className =
            "flex-1 py-3 px-4 rounded-lg transition-all duration-300 font-bold uppercase text-xs tracking-widest text-zinc-500 hover:text-orange-400";
    });
    
    document.getElementById(`sec-${tab}`).classList.remove('hidden');
    document.getElementById(`tab-${tab}`).classList.add('tab-active');
    document.getElementById('resultado').classList.add('hidden');
}

function updateFileName() {
    const fileInput = document.getElementById('file-input');
    const label = document.getElementById('file-label');
    label.innerText = fileInput.files[0]?.name || "Imagen seleccionada";
}

async function postData(endpoint, data, isFile = false) {
    const loading = document.getElementById('loading');
    const resultado = document.getElementById('resultado');
    
    loading.classList.remove('hidden');
    resultado.classList.add('hidden');
    
    try {
        let options = { method: 'POST' };
        if (isFile) {
            const formData = new FormData();
            formData.append('file', data);
            options.body = formData;
        } else {
            options.headers = { 'Content-Type': 'application/json' };
            options.body = JSON.stringify(data);
        }

        const response = await fetch(endpoint, options);
        if (!response.ok) throw new Error("Error en el servidor");
        
        const result = await response.json();
        mostrarResultado(result);
    } catch (e) {
        alert("Error al conectar con el servidor: " + e.message);
    } finally {
        loading.classList.add('hidden');
    }
}

function mostrarResultado(data) {
    console.log(data);
    const resDiv = document.getElementById('resultado');
    const resVeredicto = document.getElementById('res-veredicto');
    const resAnalisis = document.getElementById('res-analisis');
    const fuentesDiv = document.getElementById('res-fuentes');
    const resConfianza = document.getElementById('res-confianza');

    const veredicto = data.veredicto || data.veredicto_imagen || "Resultado";
    const analisis = data.analisis || data.analisis_visual || data.resumen_contenido;
    
    resDiv.classList.remove('hidden', 'border-green-500', 'border-red-500', 'border-yellow-500', 'border-orange-600');
    
    const vLower = veredicto.toLowerCase();
    if (vLower.includes("verdadero") || vLower.includes("real")) {
        resDiv.classList.add('border-green-500');
    } else if (vLower.includes("falso") || vLower.includes("manipulada") || vLower.includes("ia")) {
        resDiv.classList.add('border-red-500');
    } else {
        resDiv.classList.add('border-yellow-500');
    }

    resVeredicto.innerText = "Veredicto: " + veredicto;
    resAnalisis.innerText = analisis;
    resConfianza.innerText = "Confianza: " + (data.confianza !== undefined ? data.confianza : "N/A") + "%";
    
    const fuentes = data.fuentes_verificadas || [];
    fuentesDiv.innerHTML = fuentes.length > 0 
        ? "<strong>Fuentes encontradas:</strong><br>" + fuentes.map(f => `<a href="${f}" target="_blank" class="block underline truncate">${f}</a>`).join('')
        : "";
    
    resDiv.scrollIntoView({ behavior: 'smooth' });
}

function verificarTexto() {
    const titular = document.getElementById('titular').value;
    const contenido = document.getElementById('contenido').value;
    if(!titular || !contenido) return alert("Completa los campos");
    postData('/verificar-texto', { titular, contenido });
}

function verificarLink() {
    const url = document.getElementById('url-input').value;
    if(!url) return alert("Pega un enlace");
    postData('/verificar-link', { url });
}

function verificarImagen() {
    const file = document.getElementById('file-input').files[0];
    if (file) postData('/verificar-imagen', file, true);
    else alert("Selecciona una imagen");
}

async function cargarHistorial() {
    try {
        const response = await fetch('/historial');
        const data = await response.json();
        const contenedor = document.getElementById('historial-lista');
        
        contenedor.innerHTML = '';

        const getVeredictoColor = (veredicto) => {
            const colores = {
                'Verdadero': 'border-green-500 text-green-400',
                'Falso': 'border-red-500 text-red-400',
                'Engañoso': 'border-orange-500 text-orange-400',
                'Contradictorio': 'border-yellow-500 text-yellow-400',
                'Verificado Pero En Desarrollo': 'border-blue-500 text-blue-400'
            };
            return colores[veredicto] || 'border-zinc-700 text-zinc-400';
        };

        const totalNoticias = [...data.texto, ...data.links, ...data.imagenes]
            .sort((a, b) => new Date(b.fecha) - new Date(a.fecha))
            .slice(0, 15);

        if (totalNoticias.length === 0) {
            contenedor.innerHTML = '<div class="text-zinc-500 text-sm text-center py-6">No hay verificaciones registradas aún.</div>';
            return;
        }

        totalNoticias.forEach(item => {
            const colorClase = getVeredictoColor(item.veredicto);
            const icono = item.tipo === 'texto' ? 'fa-file-alt' : (item.tipo === 'link' ? 'fa-link' : 'fa-image');
            
            contenedor.innerHTML += `
                <div class="bg-zinc-900/50 backdrop-blur-sm p-4 rounded-2xl border-l-4 ${colorClase.split(' ')[0]} border-zinc-800 transition-all hover:bg-zinc-800/80 group">
                    <div class="flex justify-between items-start mb-2">
                        <div class="flex items-center space-x-2">
                            <i class="fas ${icono} text-zinc-500 text-xs"></i>
                            <span class="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">${item.tipo}</span>
                        </div>
                        <span class="text-[10px] text-zinc-600 font-mono">${new Date(item.fecha).toLocaleString('es-BO')}</span>
                    </div>
                    
                    <h3 class="text-zinc-200 font-medium text-sm mb-3 line-clamp-2">${item.titulo}</h3>
                    
                    <div class="flex justify-between items-center">
                        <span class="text-xs font-bold uppercase tracking-tighter ${colorClase.split(' ')[1]}">
                            ${item.veredicto}
                        </span>
                        <div class="text-[10px] text-zinc-500 bg-zinc-950 px-2 py-1 rounded-md border border-zinc-800">
                            Confianza IA: <span class="text-orange-400">${item.confianza ? (item.confianza * 100).toFixed(0) : "N/A"}%</span>
                        </div>
                    </div>
                </div>
            `;
        });
    } catch (error) {
        console.error("Error cargando historial:", error);
    }
}

document.addEventListener('DOMContentLoaded', cargarHistorial);