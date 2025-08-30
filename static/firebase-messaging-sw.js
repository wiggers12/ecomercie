// firebase-messaging-sw.js

// Importa os scripts do Firebase
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging.js");

// ATENÇÃO: Use as mesmas chaves do seu projeto, mas note que o objeto é um pouco diferente aqui.
const firebaseConfig = {
  apiKey: "AIzaSyB-rnG4cIZzEb1w_h_qmif3XPSx28ZIdaM",
  authDomain: "ecomercie-vendas.firebaseapp.com",
  projectId: "ecomercie-vendas",
  storageBucket: "ecomercie-vendas.firebasestorage.app",
  messagingSenderId: "1054540261609",
  appId: "1:1054540261609:web:90042b823220b4c73f6878",
  measurementId: "G-TNC5M9G89H"
};
// Inicializa o Firebase
const app = firebase.initializeApp(firebaseConfig);
const messaging = firebase.getMessaging(app);

// Adiciona o manipulador de mensagens em segundo plano
messaging.onBackgroundMessage((payload) => {
  console.log(
    "[firebase-messaging-sw.js] Received background message ",
    payload,
  );
  
  // Extrai o título e o corpo da notificação dos dados recebidos
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/firebase-logo.png', // Opcional: você pode adicionar um ícone
  };

  // Mostra a notificação para o usuário
  self.registration.showNotification(notificationTitle, notificationOptions);
});