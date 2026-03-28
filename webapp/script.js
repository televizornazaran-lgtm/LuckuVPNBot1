const tg = window.Telegram.WebApp;
tg.expand();

async function loadData() {
    const resp = await fetch(`http://127.0.0.1:5000/get_user_data?user_id=${tg.initDataUnsafe.user.id}`);
    const data = await resp.json();

    document.getElementById("free-period").innerText = `Бесплатный период до: ${data.free_until}`;
    document.getElementById("keys").innerText = `Ваши ключи: ${data.keys.join(", ")}`;
}

document.getElementById("get-key").addEventListener("click", async () => {
    const resp = await fetch(`http://127.0.0.1:5000/get_key?user_id=${tg.initDataUnsafe.user.id}`);
    const data = await resp.json();

    document.getElementById("free-period").innerText = `Бесплатный период до: ${data.free_until}`;
    document.getElementById("keys").innerText = `Ваши ключи: ${data.keys.join(", ")}`;
});

loadData();
