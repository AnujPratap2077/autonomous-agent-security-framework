
const cursor = document.querySelector(".fine-cursor");

if (cursor && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {

    let mouseX = 0;
    let mouseY = 0;

    let cursorX = 0;
    let cursorY = 0;

    let animationFrame = null;

    document.addEventListener("pointermove", (event) => {
        mouseX = event.clientX;
        mouseY = event.clientY;

        cursor.classList.add("visible");

        if (!animationFrame) {
            animationFrame = requestAnimationFrame(animateCursor);
        }
    });

    function animateCursor() {

        // Smooth interpolation
        cursorX += (mouseX - cursorX) * 0.22;
        cursorY += (mouseY - cursorY) * 0.22;

        cursor.style.left = `${cursorX}px`;
        cursor.style.top = `${cursorY}px`;

        // Continue while the cursor is still moving
        if (
            Math.abs(mouseX - cursorX) > 0.1 ||
            Math.abs(mouseY - cursorY) > 0.1
        ) {
            animationFrame = requestAnimationFrame(animateCursor);
        } else {
            animationFrame = null;
        }
    }

    document.addEventListener("pointerleave", () => {
        cursor.classList.remove("visible");
    });

    document.addEventListener("pointerenter", () => {
        // Cursor becomes visible on the next pointer movement
    });

}
