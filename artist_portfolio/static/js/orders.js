document.addEventListener("DOMContentLoaded", function () {
    function setupSelection(groupSelector, optionSelector) {
        const options = document.querySelectorAll(groupSelector + " " + optionSelector);

        options.forEach(option => {
            option.addEventListener("click", function () {
                options.forEach(opt => opt.classList.remove("selected"));
                options.forEach(opt => opt.classList.add("not-selected"));
                this.classList.add("selected");
                this.classList.remove("not-selected");
            });
        });
    }

    setupSelection(".delivery-options", ".delivery-option");
    setupSelection(".payment-options", ".payment-option");
});

