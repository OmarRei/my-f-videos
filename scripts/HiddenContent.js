let backToTopCount = 0;
let reverseOrderCount = 0;
let startTime = null;

function checkRevealCondition() {
    if (backToTopCount === 3 && reverseOrderCount === 2) {
        document.getElementById("hiddenContent").style.display = "block";
    }
}

document.getElementById("back-to-top-button").addEventListener("click", function() {
    if (!startTime) {
        startTime = Date.now();
    }
    backToTopCount++;
    if (Date.now() - startTime > 5000) {
        // Reset the counts and time if more than 5 seconds have passed
        backToTopCount = 1;
        reverseOrderCount = 0;
        startTime = Date.now();
    }
    checkRevealCondition();
});

document.getElementById("reverseOrder").addEventListener("click", function() {
    if (!startTime) {
        startTime = Date.now();
    }
    reverseOrderCount++;
    if (Date.now() - startTime > 5000) {
        // Reset the counts and time if more than 5 seconds have passed
        backToTopCount = 0;
        reverseOrderCount = 1;
        startTime = Date.now();
    }
    checkRevealCondition();
});
