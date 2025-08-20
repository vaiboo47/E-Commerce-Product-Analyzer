async function checkProduct() {
    const url = document.getElementById("url").value.trim();

    if (!url) {
        alert("Please enter an Amazon product URL.");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5000/api/check", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();

        // Product image
        const productImage = document.getElementById("product-image");
        productImage.src = data.image || "";
        productImage.style.display = data.image ? "block" : "none";

        // Product title
        document.getElementById("product-title").innerText = data.product_name || "Unknown Product";

        // Rating and review count
        document.getElementById("rating").innerText = data.rating ?? "N/A";
        document.getElementById("review-count").innerText = data.review_count ?? "N/A";

        // Confidence bar
        const confPercent = data.prediction === 1 ? 90 : 30;
        const confFill = document.getElementById("confidence-fill");
        confFill.style.width = confPercent + "%";
        confFill.style.background = data.prediction === 1 ? "green" : "red";
        confFill.innerText = confPercent + "%";

        // Alerts
        const alertsList = document.getElementById("alerts-list");
        alertsList.innerHTML = "";

        if (data.heuristic_reason) {
            // If it's an object with key-value pairs
            if (typeof data.heuristic_reason === "object" && !Array.isArray(data.heuristic_reason)) {
                for (const [rule, status] of Object.entries(data.heuristic_reason)) {
                    const li = document.createElement("li");
                    li.innerText = `${rule.replace(/_/g, " ")}: ${status}`;
                    li.className = status === "passed" ? "passed" : "failed";
                    alertsList.appendChild(li);
                }
            }
            // If it's already an array
            else if (Array.isArray(data.heuristic_reason)) {
                data.heuristic_reason.forEach(reason => {
                    const li = document.createElement("li");
                    li.innerText = reason;
                    alertsList.appendChild(li);
                });
            }
            // If it's a single string
            else if (typeof data.heuristic_reason === "string") {
                const li = document.createElement("li");
                li.innerText = data.heuristic_reason;
                alertsList.appendChild(li);
            }
        }

    } catch (error) {
        console.error(error);
        alert("Request failed: " + error.message);
    }
}
