/**
 * API SIMULADA (Mock API)
 * * Este archivo simula las respuestas de sus modelos de Markov y Teoría de Colas.
 * Nos permite construir la UI sin depender de que los modelos estén listos.
 * Devuelve datos hardcodeados con un pequeño retraso para simular una llamada de red.
 */

const mockData = {
  task: {
    vuelo: 'LX721',
    carrito: 'C-05',
    cajon: 3,
    tiempoEstandar: 55, // μ (micro) - Salida del Modelo de Colas
    items: [
      { id: 'SNK-001', nombre: 'Snack Box Economy', qtyRequerida: 32 },
      { id: 'JUC-003', nombre: 'Jugo de Naranja', qtyRequerida: 15 },
    ]
  },
  dashboards: {
    productividad: {
      eficienciaGeneral: 92,
      estadoCola: 'SALUDABLE',
      esperaPromedio: 0.8, // en minutos
      empleadosRecomendados: 5, // s (salida del modelo)
      empleadosActuales: 5,
    },
    consumo: {
      tasaDesperdicio: 15,
      estadoModelo: 'ESTABLE (15,000 iteraciones)',
      ultimaActualizacion: 'Hoy 06:00 AM',
      politicaEjemplo: 'Ruta ZRH-JFK (Vino): Cargar 2 [S1]',
    },
    caducidad: {
      alertaCritica: '¡ALERTA! 3 Lotes [S_CRÍTICO] vencen en 48h.',
      desechadosHoy: 120,
      inventario: [
        { estado: 'S_VÁLIDO', qty: 15000 },
        { estado: 'S_CRÍTICO', qty: 350 },
        { estado: 'S_VENCIDO', qty: 80 },
      ]
    }
  }
};

// Lógica de simulación FEFO
const lotesCriticos = ['LOTE-CRITICO-123'];
const lotesValidos = ['LOTE-VALIDO-456'];
const lotesVencidos = ['LOTE-VENCIDO-789'];

// Simula una llamada de red
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * (Operador) Obtiene la siguiente tarea de empaque.
 * Simula la salida de los modelos de Consumo y Productividad.
 */
export const getPackingTask = async () => {
  await delay(400);
  return mockData.task;
};

/**
 * (Operador) Obtiene un trabajo de empaque completo con múltiples cajones.
 * Versión extendida para la pantalla rediseñada.
 * Ahora devuelve 16 cajones para coincidir con el modelo 3D de doble lado (8 front + 8 back).
 */
export const getPackingJob = async () => {
  // Simulación de una llamada de red
  await delay(500);
  
  // Datos simulados
  return {
    vuelo: 'LX721',
    destino: 'ZRH-JFK',
    tiempoEstandar: 480, // 8 minutos (μ de nuestro modelo)
    cajones: [
      // FRONT SIDE (8 drawers)
      { id: 'drawer-1', nombre: 'Cajón 1: Snacks (ECON)', contenido: '32 Snacks, 15 Jugos' },
      { id: 'drawer-2', nombre: 'Cajón 2: Snacks (ECON)', contenido: '32 Snacks, 15 Jugos' },
      { id: 'drawer-3', nombre: 'Cajón 3: Bebidas (PREM)', contenido: '8 Vinos, 10 Cervezas' },
      { id: 'drawer-4', nombre: 'Cajón 4: Bebidas (PREM)', contenido: '8 Vinos, 10 Cervezas' },
      { id: 'drawer-5', nombre: 'Cajón 5: Amenidades', contenido: '20 Kits Dentales, 15 Antifaces' },
      { id: 'drawer-6', nombre: 'Cajón 6: Comida Fría', contenido: '12 Ensaladas, 12 Postres' },
      { id: 'drawer-7', nombre: 'Cajón 7: Vacío', contenido: 'N/A' },
      { id: 'drawer-8', nombre: 'Cajón 8: Vacío', contenido: 'N/A' },
      // BACK SIDE (8 drawers)
      { id: 'drawer-9', nombre: 'Cajón 9: Snacks (BUS)', contenido: '24 Snacks, 12 Bebidas' },
      { id: 'drawer-10', nombre: 'Cajón 10: Comida Caliente', contenido: '16 Platos Calientes' },
      { id: 'drawer-11', nombre: 'Cajón 11: Bebidas (BUS)', contenido: '15 Vinos, 12 Licores' },
      { id: 'drawer-12', nombre: 'Cajón 12: Postres', contenido: '20 Pasteles, 18 Frutas' },
      { id: 'drawer-13', nombre: 'Cajón 13: Cubiertos', contenido: '50 Sets Cubiertos' },
      { id: 'drawer-14', nombre: 'Cajón 14: Servilletas', contenido: '100 Servilletas' },
      { id: 'drawer-15', nombre: 'Cajón 15: Vacío', contenido: 'N/A' },
      { id: 'drawer-16', nombre: 'Cajón 16: Vacío', contenido: 'N/A' },
    ],
  };
};

/**
 * (Operador) Simula la validación de un lote escaneado.
 * Esta es la lógica FEFO que bloquea al usuario.
 */
export const validateLoteFEFO = async (loteQR) => {
  await delay(200);
  
  // Simulación de Límite (Regla FEFO)
  if (lotesValidos.includes(loteQR)) {
    // El usuario escaneó un lote válido, PERO debemos checar si existe uno crítico.
    // En esta simulación, asumimos que SÍ existe uno crítico.
    return {
      status: 'error',
      code: 'FEFO_VIOLATION',
      message: '¡ERROR! Use primero el lote [LOTE-CRITICO-123] que vence pronto.',
      loteCorrecto: 'LOTE-CRITICO-123'
    };
  }

  if (lotesCriticos.includes(loteQR)) {
    return {
      status: 'success',
      code: 'FEFO_OK',
      message: 'Lote Crítico OK'
    };
  }
  
  if (lotesVencidos.includes(loteQR)) {
     return {
      status: 'error',
      code: 'VENCIDO',
      message: '¡LOTE VENCIDO! No se puede cargar.'
    };
  }

  return { status: 'error', code: 'NOT_FOUND', message: 'Lote no encontrado' };
};

/**
 * (Operador) Simula la validación de un lote en Retorno Asistido.
 */
export const validateReturnLote = async (loteQR) => {
  await delay(200);

  if (lotesValidos.includes(loteQR) || lotesCriticos.includes(loteQR)) {
    return {
      status: 'success',
      code: 'RETURN_OK',
      message: 'LOTE OK. Devolver a Almacén.'
    };
  }

  if (lotesVencidos.includes(loteQR)) {
    return {
      status: 'error',
      code: 'VENCIDO',
      message: '¡ALERTA CADUCIDAD! Lote vencido. Desechar.'
    };
  }
  
  return { status: 'error', code: 'NOT_FOUND', message: 'Lote no encontrado' };
};


/**
 * (Operador) Obtiene los detalles de un producto por su EAN/código de barras.
 */
export const getProductDetails = async (ean) => {
  await delay(300);
  
  // Simulación de base de datos de productos
  const productos = {
    '7501234567890': { ean: '7501234567890', nombre: 'Snack Box Economy' },
    '7501234567891': { ean: '7501234567891', nombre: 'Jugo de Naranja' },
    '7501234567892': { ean: '7501234567892', nombre: 'Sándwich de Jamón' },
    '7501234567893': { ean: '7501234567893', nombre: 'Galletas Chocolate' },
  };
  
  return productos[ean] || null;
};

/**
 * (Operador) Registra un nuevo lote en el sistema.
 */
export const registerNewLote = async (ean, cantidad, fechaCaducidad) => {
  await delay(400);
  
  // Validaciones básicas
  if (!ean || !cantidad || !fechaCaducidad) {
    return {
      status: 'error',
      message: 'Faltan datos obligatorios'
    };
  }
  
  if (cantidad <= 0) {
    return {
      status: 'error',
      message: 'La cantidad debe ser mayor a 0'
    };
  }
  
  // Simular registro exitoso
  const loteId = `LOTE-${Date.now()}`;
  return {
    status: 'success',
    message: 'Lote registrado correctamente',
    loteId: loteId
  };
};


/**
 * (Operador) Obtiene el historial de actividades del operador
 */
export const getOperadorHistory = async (operadorNombre) => {
  await delay(400);
  
  // Datos simulados de historial
  const history = [
    {
      id: 'ACT-001',
      tipo: 'Empaque Guiado',
      vuelo: 'LX721',
      destino: 'ZRH-JFK',
      tiempoEstimado: 480, // 8 minutos
      tiempoReal: 455, // 7:35 minutos
      eficiencia: 105.5, // (480/455) * 100
      fecha: new Date(Date.now() - 2 * 60 * 60 * 1000), // Hace 2 horas
      estado: 'completed',
    },
    {
      id: 'ACT-002',
      tipo: 'Registro de Lote',
      producto: 'Snack Box Economy',
      cantidad: 150,
      tiempoReal: 180, // 3 minutos
      fecha: new Date(Date.now() - 4 * 60 * 60 * 1000), // Hace 4 horas
      estado: 'completed',
    },
    {
      id: 'ACT-003',
      tipo: 'Empaque Guiado',
      vuelo: 'LX518',
      destino: 'GVA-LHR',
      tiempoEstimado: 420,
      tiempoReal: 495, // Tardó más
      eficiencia: 84.8,
      fecha: new Date(Date.now() - 6 * 60 * 60 * 1000), // Hace 6 horas
      estado: 'completed',
    },
    {
      id: 'ACT-004',
      tipo: 'Retorno Asistido',
      itemsProcesados: 24,
      tiempoReal: 360, // 6 minutos
      fecha: new Date(Date.now() - 8 * 60 * 60 * 1000), // Hace 8 horas
      estado: 'completed',
    },
    {
      id: 'ACT-005',
      tipo: 'Empaque Guiado',
      vuelo: 'LX322',
      destino: 'ZRH-BCN',
      tiempoEstimado: 360,
      tiempoReal: 342,
      eficiencia: 105.3,
      fecha: new Date(Date.now() - 24 * 60 * 60 * 1000), // Hace 1 día
      estado: 'completed',
    },
  ];
  
  return history;
};

/**
 * (Operador) Registra una nueva actividad completada
 */
export const saveActivity = async (activityData) => {
  await delay(300);
  
  console.log('💾 Guardando actividad:', activityData);
  
  return {
    status: 'success',
    message: 'Actividad registrada correctamente',
    activityId: `ACT-${Date.now()}`,
  };
};

/**
 * (Operador) Guarda un lote completo en la base de datos
 * Recibe los campos: QR_code, Object_name, LoteID, Fecha_de_caducidad, Cantidad
 */
export const saveLoteToDatabase = async (loteData) => {
  await delay(500);
  
  // Validaciones
  if (!loteData.QR_code || !loteData.Object_name || !loteData.LoteID || 
      !loteData.Fecha_de_caducidad || !loteData.Cantidad) {
    return {
      status: 'error',
      message: 'Todos los campos son obligatorios'
    };
  }
  
  if (loteData.Cantidad <= 0) {
    return {
      status: 'error',
      message: 'La cantidad debe ser mayor a 0'
    };
  }
  
  // Simular actualización en base de datos
  console.log('📦 Guardando lote en la base de datos:', {
    QR_code: loteData.QR_code,
    Object_name: loteData.Object_name,
    LoteID: loteData.LoteID,
    Fecha_de_caducidad: loteData.Fecha_de_caducidad,
    Cantidad: loteData.Cantidad,
    timestamp: new Date().toISOString()
  });
  
  return {
    status: 'success',
    message: 'Lote guardado correctamente en la base de datos',
    recordId: loteData.QR_code
  };
};

/**
 * (Operador - Empaque Guiado) Obtiene el trabajo completo de empaque con todos los cajones
 * Cada vuelo puede requerir un número diferente de cajones (7, 8, 12, 16, etc.)
 */
export const getDrawerJob = async () => {
  await delay(600);
  
  // Simulación de diferentes vuelos con diferentes cantidades de cajones
  const flightConfigs = [
    {
      flight: 'LX721',
      route: 'ZRH → JFK',
      drawerCount: 16, // Vuelo largo - todos los cajones
    },
    {
      flight: 'LX518',
      route: 'GVA → LHR',
      drawerCount: 8, // Vuelo corto - solo lado frontal
    },
    {
      flight: 'LX322',
      route: 'ZRH → BCN',
      drawerCount: 12, // Vuelo medio - 12 cajones
    },
  ];
  
  // Seleccionar configuración aleatoria (o puedes cambiar la lógica)
  const config = flightConfigs[0]; // Por ahora usar el primero (16 cajones)
  
  // Generar cajones según la configuración
  const allDrawers = [
    // FRONT SIDE (8 drawers)
    { 
      id: 'drawer-1', 
      name: 'Cajón 1 (Frontal)', 
      description: 'Bebidas Economy',
      side: 'front',
      position: 0
    },
    { 
      id: 'drawer-2', 
      name: 'Cajón 2 (Frontal)', 
      description: 'Snacks Economy',
      side: 'front',
      position: 1
    },
    { 
      id: 'drawer-3', 
      name: 'Cajón 3 (Frontal)', 
      description: 'Bebidas Premium',
      side: 'front',
      position: 2
    },
    { 
      id: 'drawer-4', 
      name: 'Cajón 4 (Frontal)', 
      description: 'Bebidas Premium',
      side: 'front',
      position: 3
    },
    { 
      id: 'drawer-5', 
      name: 'Cajón 5 (Frontal)', 
      description: 'Amenidades',
      side: 'front',
      position: 4
    },
    { 
      id: 'drawer-6', 
      name: 'Cajón 6 (Frontal)', 
      description: 'Comida Fría',
      side: 'front',
      position: 5
    },
    { 
      id: 'drawer-7', 
      name: 'Cajón 7 (Frontal)', 
      description: 'Snacks Business',
      side: 'front',
      position: 6
    },
    { 
      id: 'drawer-8', 
      name: 'Cajón 8 (Frontal)', 
      description: 'Comida Caliente',
      side: 'front',
      position: 7
    },
    // BACK SIDE (8 drawers)
    { 
      id: 'drawer-9', 
      name: 'Cajón 9 (Trasero)', 
      description: 'Bebidas Business',
      side: 'back',
      position: 0
    },
    { 
      id: 'drawer-10', 
      name: 'Cajón 10 (Trasero)', 
      description: 'Snacks Premium',
      side: 'back',
      position: 1
    },
    { 
      id: 'drawer-11', 
      name: 'Cajón 11 (Trasero)', 
      description: 'Alcohol Premium',
      side: 'back',
      position: 2
    },
    { 
      id: 'drawer-12', 
      name: 'Cajón 12 (Trasero)', 
      description: 'Postres',
      side: 'back',
      position: 3
    },
    { 
      id: 'drawer-13', 
      name: 'Cajón 13 (Trasero)', 
      description: 'Cubiertos',
      side: 'back',
      position: 4
    },
    { 
      id: 'drawer-14', 
      name: 'Cajón 14 (Trasero)', 
      description: 'Servilletas',
      side: 'back',
      position: 5
    },
    { 
      id: 'drawer-15', 
      name: 'Cajón 15 (Trasero)', 
      description: 'Vasos y Platos',
      side: 'back',
      position: 6
    },
    { 
      id: 'drawer-16', 
      name: 'Cajón 16 (Trasero)', 
      description: 'Utensilios',
      side: 'back',
      position: 7
    },
  ];
  
  // Tomar solo los cajones necesarios para este vuelo
  const drawersForFlight = allDrawers.slice(0, config.drawerCount);
  
  return {
    jobId: 'JOB-' + Date.now(),
    flight: config.flight,
    route: config.route,
    estimatedTime: 480, // segundos (8 minutos)
    status: false, // FALSE = no completado, TRUE = completado
    locked: false, // Se bloquea cuando se completa
    requiredDrawers: config.drawerCount, // Número de cajones requeridos
    drawers: drawersForFlight,
  };
};

/**
 * (Operador - Empaque Guiado) Valida el QR de un cajón y devuelve su contenido
 */
export const validateDrawerQR = async (qrCode, drawerId) => {
  await delay(400);
  
  // Simulación de base de datos de cajones
  const drawerDatabase = {
    'QR-DRAWER-001': {
      id: 'drawer-1',
      name: 'Cajón 1: Bebidas Economy (Frontal)',
      type: 'Bebidas',
      class: 'ECON',
      items: [
        { id: 'item-1', name: 'Coca Cola 330ml', quantity: 24 },
        { id: 'item-2', name: 'Fanta 330ml', quantity: 18 },
        { id: 'item-3', name: 'Sprite 330ml', quantity: 12 },
      ]
    },
    'QR-DRAWER-002': {
      id: 'drawer-2',
      name: 'Cajón 2: Snacks Economy (Frontal)',
      type: 'Snacks',
      class: 'ECON',
      items: [
        { id: 'item-4', name: 'Papas Fritas 50g', quantity: 32 },
        { id: 'item-5', name: 'Galletas Chocolate', quantity: 20 },
        { id: 'item-6', name: 'Mix de Nueces', quantity: 15 },
      ]
    },
    'QR-DRAWER-003': {
      id: 'drawer-3',
      name: 'Cajón 3: Bebidas Premium (Frontal)',
      type: 'Bebidas',
      class: 'PREM',
      items: [
        { id: 'item-7', name: 'Jugo Naranja Premium', quantity: 12 },
        { id: 'item-8', name: 'Agua Mineral', quantity: 16 },
        { id: 'item-9', name: 'Café Espresso', quantity: 8 },
      ]
    },
    'QR-DRAWER-004': {
      id: 'drawer-4',
      name: 'Cajón 4: Bebidas Premium (Frontal)',
      type: 'Bebidas',
      class: 'PREM',
      items: [
        { id: 'item-10', name: 'Té Selección', quantity: 10 },
        { id: 'item-11', name: 'Jugo Manzana', quantity: 14 },
        { id: 'item-12', name: 'Smoothie Verde', quantity: 8 },
      ]
    },
    'QR-DRAWER-005': {
      id: 'drawer-5',
      name: 'Cajón 5: Amenidades (Frontal)',
      type: 'Amenidades',
      class: 'ECON',
      items: [
        { id: 'item-13', name: 'Kit Dental', quantity: 20 },
        { id: 'item-14', name: 'Antifaz', quantity: 15 },
        { id: 'item-15', name: 'Tapones de Oídos', quantity: 15 },
      ]
    },
    'QR-DRAWER-006': {
      id: 'drawer-6',
      name: 'Cajón 6: Comida Fría (Frontal)',
      type: 'Comida',
      class: 'ECON',
      items: [
        { id: 'item-16', name: 'Ensalada César', quantity: 12 },
        { id: 'item-17', name: 'Postre Tiramisu', quantity: 12 },
        { id: 'item-18', name: 'Fruta Fresca', quantity: 10 },
      ]
    },
    'QR-DRAWER-007': {
      id: 'drawer-7',
      name: 'Cajón 7: Snacks Business (Frontal)',
      type: 'Snacks',
      class: 'BUS',
      items: [
        { id: 'item-19', name: 'Snack Mix Premium', quantity: 24 },
        { id: 'item-20', name: 'Chocolate Lindt', quantity: 12 },
      ]
    },
    'QR-DRAWER-008': {
      id: 'drawer-8',
      name: 'Cajón 8: Comida Caliente (Frontal)',
      type: 'Comida',
      class: 'BUS',
      items: [
        { id: 'item-21', name: 'Pasta Penne', quantity: 16 },
        { id: 'item-22', name: 'Pollo al Limón', quantity: 14 },
      ]
    },
    // BACK SIDE DRAWERS (9-16)
    'QR-DRAWER-009': {
      id: 'drawer-9',
      name: 'Cajón 9: Bebidas Business (Trasero)',
      type: 'Bebidas',
      class: 'BUS',
      items: [
        { id: 'item-23', name: 'Champagne Mini', quantity: 12 },
        { id: 'item-24', name: 'Agua Perrier', quantity: 18 },
        { id: 'item-25', name: 'Jugo Premium', quantity: 10 },
      ]
    },
    'QR-DRAWER-010': {
      id: 'drawer-10',
      name: 'Cajón 10: Snacks Premium (Trasero)',
      type: 'Snacks',
      class: 'PREM',
      items: [
        { id: 'item-26', name: 'Caviar Snack', quantity: 8 },
        { id: 'item-27', name: 'Queso Gourmet', quantity: 10 },
        { id: 'item-28', name: 'Crackers Artesanales', quantity: 15 },
      ]
    },
    'QR-DRAWER-011': {
      id: 'drawer-11',
      name: 'Cajón 11: Alcohol Premium (Trasero)',
      type: 'Alcohol',
      class: 'PREM',
      items: [
        { id: 'item-29', name: 'Vino Tinto 187ml', quantity: 8 },
        { id: 'item-30', name: 'Vino Blanco 187ml', quantity: 8 },
        { id: 'item-31', name: 'Cerveza Premium', quantity: 10 },
      ]
    },
    'QR-DRAWER-012': {
      id: 'drawer-12',
      name: 'Cajón 12: Postres (Trasero)',
      type: 'Postres',
      class: 'PREM',
      items: [
        { id: 'item-32', name: 'Mousse Chocolate', quantity: 15 },
        { id: 'item-33', name: 'Tarta de Limón', quantity: 12 },
        { id: 'item-34', name: 'Macarons', quantity: 20 },
      ]
    },
    'QR-DRAWER-013': {
      id: 'drawer-13',
      name: 'Cajón 13: Cubiertos (Trasero)',
      type: 'Utensilios',
      class: 'ECON',
      items: [
        { id: 'item-35', name: 'Set Cubiertos', quantity: 50 },
        { id: 'item-36', name: 'Cuchillo Plástico', quantity: 30 },
        { id: 'item-37', name: 'Tenedor Plástico', quantity: 30 },
      ]
    },
    'QR-DRAWER-014': {
      id: 'drawer-14',
      name: 'Cajón 14: Servilletas (Trasero)',
      type: 'Utensilios',
      class: 'ECON',
      items: [
        { id: 'item-38', name: 'Servilletas Papel', quantity: 100 },
        { id: 'item-39', name: 'Servilletas Tela', quantity: 50 },
      ]
    },
    'QR-DRAWER-015': {
      id: 'drawer-15',
      name: 'Cajón 15: Vasos y Platos (Trasero)',
      type: 'Utensilios',
      class: 'ECON',
      items: [
        { id: 'item-40', name: 'Vasos Plástico', quantity: 60 },
        { id: 'item-41', name: 'Platos Desechables', quantity: 40 },
        { id: 'item-42', name: 'Tazas Café', quantity: 30 },
      ]
    },
    'QR-DRAWER-016': {
      id: 'drawer-16',
      name: 'Cajón 16: Utensilios (Trasero)',
      type: 'Utensilios',
      class: 'ECON',
      items: [
        { id: 'item-43', name: 'Abrelatas', quantity: 10 },
        { id: 'item-44', name: 'Sacacorchos', quantity: 8 },
        { id: 'item-45', name: 'Palillos', quantity: 100 },
      ]
    },
  };
  
  // Validar que el QR exista
  if (!drawerDatabase[qrCode]) {
    return {
      status: 'error',
      message: 'QR no válido. Este código no corresponde a ningún cajón.'
    };
  }
  
  // Validar que el QR corresponda al cajón correcto
  const drawerData = drawerDatabase[qrCode];
  if (drawerData.id !== drawerId) {
    return {
      status: 'error',
      message: `QR incorrecto. Este código pertenece a ${drawerData.name}, no a ${drawerId}.`
    };
  }
  
  return {
    status: 'success',
    data: drawerData
  };
};

/**
 * (Operador - Empaque Guiado) Guarda los datos de un cajón completado
 */
export const saveDrawerData = async (drawerData) => {
  await delay(500);
  
  console.log('💾 Guardando cajón:', {
    drawerId: drawerData.drawerId,
    qrCode: drawerData.qrCode,
    itemCount: drawerData.items.length,
    completedAt: drawerData.completedAt
  });
  
  return {
    status: 'success',
    message: 'Cajón guardado correctamente'
  };
};

/**
 * (Operador - Empaque Guiado) Completa el trabajo de empaque (todos los cajones)
 */
export const completePackingJob = async (jobId, drawers) => {
  await delay(800);
  
  console.log('🎉 Completando trabajo:', {
    jobId: jobId,
    totalDrawers: drawers.length,
    completedDrawers: drawers.filter(d => d.status === 'completed').length,
    completedAt: new Date().toISOString()
  });
  
  // Cambiar el estado del trabajo de FALSE a TRUE (completado)
  // En una aplicación real, esto actualizaría la base de datos
  console.log('✅ Estado del trabajo cambiado: FALSE → TRUE');
  console.log('🔒 Trabajo bloqueado - No se pueden editar los cajones');
  
  return {
    status: 'success',
    message: 'Trabajo completado exitosamente',
    jobStatus: 'completed', // FALSE → TRUE
    locked: true
  };
};

/**
 * (Operador - Empaque Guiado) Verifica si hay trabajos disponibles
 */
export const checkJobAvailability = async () => {
  await delay(300);
  
  // Simulación: 70% de probabilidad de que haya trabajo disponible
  const available = Math.random() > 0.3;
  
  return {
    available: available,
    message: available 
      ? 'Hay trabajos pendientes en la cola' 
      : 'No hay trabajos disponibles en este momento'
  };
};

/**
 * (Supervisor) Obtiene todos los datos de los dashboards.
 */
export const getDashboardData = async () => {
  await delay(500);
  return mockData.dashboards;
};
