document.addEventListener('DOMContentLoaded', () => {
    const iconDisplay = document.getElementById('icon-display');
    const iconInput = document.getElementById('icon'); // Hidden input
    const emojiPicker = document.getElementById('emoji-picker');

    const emojis = [
        // Smileys & People
        '😀', '😂', '😊', '🤔', '🤫', '🤗', '🤩', '🥳', '👨‍💻', '👩‍💻', '👨‍🎓', '👩‍🎓', '👨‍🏫', '👩‍🏫', '👨‍🍳', '👩‍🍳', '👨‍🎨', '👩‍🎨', '👨‍🚀', '👩‍🚀',
        // Animals & Nature
        '🐶', '🐱', '🐭', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷', '🐸', '🐵', '🐔', '🐧', '🐦', '🦉', '🦋', '🐛', '🐌', '🐞', '🐜', '🦗', '🕷️', '🐢', '🐍', '🦎', '🐙', '🐠', '🐡', '🐬', '🐳', '🌊', '🌋', '☀️', '🌙', '⭐', '🌸', '🌹', '🌻', '🌲', '🌳', '🌵', '🍁', '🍄',
        // Food & Drink
        '🍎', '🍌', '🍇', '🍓', '🍒', '🍑', '🍍', '🥝', '🥑', '🥦', '🥕', '🌽', '🌶️', '🍄', '🍕', '🍔', '🍟', '🌮', '🍜', '🍣', '🍦', '🍩', '🍪', '🎂', '☕', '🍵', '🥤', '🍺', '🍷',
        // Activities & Sports
        '⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎱', '🏓', '🏸', '🏒', '🥊', '🥋', '🥅', '⛳', '⛸️', '🎣', '🎽', '🎿', '⛷️', '🏂', '🤺', '🤾', '🤸', '⛹️', '🏋️', '🚴', '🚵', '🧗', '🧘', '🎯', '🎮', '🎲', '🎰', '🎨', '🎭', '🎤', '🎧', '🎼', '🎹', '🥁', '🎷', '🎺', '🎸', '🎻', '🎬', '📚', '📖',
        // Travel & Places
        '🚗', '🚕', '🚌', '🚓', '🚑', '🚚', '🚲', '🛵', '✈️', '🚀', '🛸', '⚓', '⛽', '🏠', '🏢', '🏥', '🏦', '🏨', '🏫', '🏭', '🏰', '🗼', '🗽', '🗿', '🗺️', '🏕️', '🏖️', '🏜️', '🏞️',
        // Objects
        '📱', '💻', '🖥️', '🖨️', '🖱️', '💾', '💿', '📀', '📷', '📹', '📺', '💡', '🔦', '🔧', '🔨', '🔩', '🔫', '💣', '🔪', '🛡️', '💰', '💎', '📈', '📊', '📌', '📍', '📎', '📏', '📐', '✂️', '📝', '✏️', '✒️', '🖌️', '🗑️', '🔑', '🔒', '🔓', '🔔', '🎁', '🎈', '🎉', '💌', '📦', '📅', '🗓️', '⏱️', '⏳', '💡', '⚖️', '⚙️', '🔗', '🧪', '🧫', '🧬', '🔬', '🔭',
        // Symbols
        '❤️', '💔', '💯', '✅', '✔️', '☑️', '➕', '➖', '➗', '✖️', '💲', '🪙', '📉', '📈', '⚠️', '❓', '❗', '♻️', '♿', '⚓', '⚡', '⚙️', '⚛️', '🔑', '💡', '🔥', '💧', '🌍', '✔️' // Added 🪙 (coin) as it's a common symbol
    ];

    function populatePicker() {
        if (!emojiPicker) return;
        emojis.forEach(emoji => {
            const emojiElement = document.createElement('span');
            emojiElement.classList.add('emoji-item');
            emojiElement.textContent = emoji;
            emojiElement.setAttribute('role', 'button');
            emojiElement.setAttribute('tabindex', '0');
            emojiElement.dataset.emoji = emoji;
            emojiElement.addEventListener('click', () => selectEmoji(emoji));
            emojiElement.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    selectEmoji(emoji);
                }
            });
            emojiPicker.appendChild(emojiElement);
        });
    }

    function selectEmoji(emoji) {
        if (iconDisplay && iconInput) {
            iconDisplay.textContent = emoji;
            iconInput.value = emoji;
        }
        togglePicker(false); // Hide picker after selection
    }

    function togglePicker(forceShow) {
        if (!emojiPicker) return;
        const isVisible = emojiPicker.classList.contains('picker-visible');
        if (typeof forceShow === 'boolean') {
            if (forceShow) {
                emojiPicker.classList.add('picker-visible');
            } else {
                emojiPicker.classList.remove('picker-visible');
            }
        } else {
            emojiPicker.classList.toggle('picker-visible');
        }
    }

    if (iconDisplay) {
        iconDisplay.addEventListener('click', () => togglePicker());
        iconDisplay.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                togglePicker();
            }
        });
    }

    // Close picker if clicked outside
    document.addEventListener('click', (event) => {
        if (!emojiPicker || !iconDisplay) return;
        const isClickInsidePicker = emojiPicker.contains(event.target);
        const isClickOnDisplayButton = iconDisplay.contains(event.target);

        if (!isClickInsidePicker && !isClickOnDisplayButton && emojiPicker.style.display !== 'none') {
            togglePicker(false);
        }
    });

    populatePicker();
});
