document.addEventListener("DOMContentLoaded", () => {
    const compareBtn = document.getElementById("compare-btn");
    const cityInput = document.getElementById("city");
    const resultP = document.getElementById("comparison-result");

    if (compareBtn) {
        compareBtn.addEventListener("click", async () => {
            const city = cityInput.value.trim();
            if (!city) {
                resultP.textContent = "Please enter a city name first.";
                return;
            }

            const userTime = new Date().toISOString();

            const response = await fetch("/compare-time", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ city: city, user_time: userTime })
            });

            const data = await response.json();

            if (data.error) {
                resultP.textContent = `Error: ${data.error}`;
            } else {
                resultP.textContent = `City time: ${data.city_time}. Time difference: ${data.time_difference}`;
            }
        });
    }
});
