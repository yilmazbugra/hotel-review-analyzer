
document.getElementById("reviewForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    const reviewText = document.getElementById("reviews").value;
    const reviews = reviewText.split("\n").filter(r => r.trim() !== "");
    const response = await fetch("/analyze_reviews", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ reviews })
    });
    const result = await response.json();
    document.getElementById("output").textContent = JSON.stringify(result, null, 2);
});
