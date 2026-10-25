# Rotina do Gabriel — app Android

App de rotina noturna com cronômetro, estudos para concurso, treinos e histórico.
Os avisos (lembretes e fim de cada etapa) chegam **mesmo com o app fechado**.

## Como gerar o APK (sem instalar nada no computador)

1. Crie uma conta grátis em github.com e um repositório novo (pode ser público; o código não tem dados pessoais).
2. Envie todos os arquivos desta pasta para o repositório (botão **Add file → Upload files**, arraste a pasta inteira, inclusive `.github`).
3. Abra a aba **Actions**. O build "Gerar APK" roda sozinho e leva uns 5 minutos.
4. Quando ficar verde, abra **Releases → Rotina do Gabriel — última versão** e baixe `RotinaDoGabriel.apk`.

## Como instalar no Android

1. Abra o `RotinaDoGabriel.apk` no celular (pelo Chrome, Drive ou WhatsApp).
2. Se o Android pedir, permita "instalar apps desta fonte".
3. Abra o app, confirme os horários e **permita as notificações**.
4. Recomendado: Configurações → Apps → Rotina do Gabriel → Bateria → **Sem restrições** (Samsung/Xiaomi às vezes seguram avisos para economizar bateria).

## Atualizar

Mude o app em `src/rotina-gabriel.html`, rode `python3 build-www.py src/rotina-gabriel.html www/index.html` e envie para o GitHub.
Um APK novo é gerado. Ele instala por cima do antigo **sem apagar os dados**, porque a assinatura vem sempre do segredo `ANDROID_KEYSTORE` (Settings → Secrets and variables → Actions). Guarde uma cópia desse segredo.

## Rodar localmente (opcional, para quem programa)

Precisa de Node 22, JDK 21 e Android SDK:

    npm ci
    npx cap sync android
    cd android && ./gradlew assembleRelease
