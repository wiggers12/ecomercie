// --- Importa Firebase no modo compat (garante suporte em navegadores antigos) ---
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js");

// --- Configuração do Firebase (igual ao admin.html) ---
firebase.initializeApp({
  apiKey: "AIzaSyB-rnG4cIZzEb1w_h_qmif3XPSx28ZIdaM",
  authDomain: "ecomercie-vendas.firebaseapp.com",
  projectId: "ecomercie-vendas",
  storageBucket: "ecomercie-vendas.firebasestorage.app",
  messagingSenderId: "1054540261609",
  appId: "1:1054540261609:web:90042b823220b4c73f6878",
  measurementId: "G-TNC5M9G89H"
});

// --- Inicializa messaging ---
const messaging = firebase.messaging();

// --- Listener para mensagens em segundo plano ---
messaging.onBackgroundMessage((payload) => {
  console.log("📩 [SW] Mensagem recebida em segundo plano:", payload);

  const notificationTitle = payload.notification?.title || "Nova Notificação";
  const notificationOptions = {
    body: payload.notification?.body || "Você recebeu uma nova mensagem",
    icon: "/icon-192.png",
    badge: "/icon-192.png",
    data: { url: "/admin" } // 🔹 Ao clicar, leva para o painel admin
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// --- Evento de clique na notificação ---
self.addEventListener("notificationclick", function(event) {
  console.log("🖱️ [SW] Notificação clicada:", event);
  event.notification.close();

  // 🔹 Garante que abre o painel
  event.waitUntil(
    clients.matchAll({ type: "window" }).then((clientList) => {
      for (const client of clientList) {
        if (client.url.includes("/admin") && "focus" in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow("/admin");
      }
    })
  );
});

// --- Debug extra: mostra quando o SW é ativado ---
self.addEventListener("install", () => {
  console.log("✅ [SW] Instalado com sucesso");
});
self.addEventListener("activate", () => {
  console.log("🚀 [SW] Ativo e pronto para receber push");
});