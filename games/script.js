let previousGames = [];  // Для хранения индексов предыдущего обновления
let games;  // Храним данные об играх вне функции для повторного использования
let preloadedImages = [];  // Храним предварительно загруженные изображения

// Подгружаем данные из JSON
async function fetchWizardData() {
    const response = await fetch('Wizard_Data.json');
    const data = await response.json();
    games = data.segments[0].hits;
    return games;
}

// Функция для получения случайного индекса без повторений
function getRandomUniqueIndex(arr, usedIndices) {
    let randomIndex;
    do {
        randomIndex = Math.floor(Math.random() * arr.length);
    } while (usedIndices.includes(randomIndex));
    usedIndices.push(randomIndex);
    return randomIndex;
}

// Заменяем изображения на случайные картинки и добавляем кликабельность
async function replaceImages() {
    games = await fetchWizardData();
    const images = document.querySelectorAll('.game-section .game-icon img');
    
    const usedIndices = [];  // Массив для хранения уже использованных индексов

    images.forEach((img) => {
        // Получаем случайный индекс игры, которая ещё не была выбрана
        const randomIndex = getRandomUniqueIndex(games, usedIndices);
        const randomGame = games[randomIndex];
        const image512x512 = randomGame.Assets.find(asset => asset.includes('512x512'));
        const gameUrl = randomGame['Game URL'];  // Получаем URL игры

        if (image512x512) {
            const newImg = new Image();
            newImg.src = image512x512;

            newImg.onload = () => {
                img.src = image512x512;
                img.dataset.gameUrl = gameUrl;  // Сохраняем Game URL в атрибуте
            };

            newImg.onerror = () => {
                img.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wcAAwAB/0GtWfgAAAAASUVORK5CYII=";
            };
        }

        // Добавляем событие клика, чтобы при нажатии открыть iframe
        img.addEventListener('click', () => {
            openGameInIframe(gameUrl);
        });
    });

    preloadNewIcons();  // Загружаем следующий набор иконок
}

// Предварительная загрузка нового набора иконок
function preloadNewIcons() {
    preloadedImages = [];  // Очищаем предыдущие загруженные изображения
    const usedIndices = [...previousGames];  // Для контроля повторений

    for (let i = 0; i < 12; i++) {  // Примерно столько же иконок как на экране
        const randomIndex = getRandomUniqueIndex(games, usedIndices);
        const randomGame = games[randomIndex];
        const image512x512 = randomGame.Assets.find(asset => asset.includes('512x512'));

        if (image512x512) {
            const img = new Image();
            img.src = image512x512;
            preloadedImages.push({ img, gameUrl: randomGame['Game URL'] });
        }
    }
}

// Используем IntersectionObserver для ленивой загрузки изображений
function observeImages() {
    const images = document.querySelectorAll('.game-section .game-icon img');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.getAttribute('data-src')) {
                    img.src = img.getAttribute('data-src');
                }
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => observer.observe(img));
}

// Функция для обновления иконок при клике на refresh
function updateGameIcons() {
    const images = document.querySelectorAll('.game-section .game-icon img');
    
    const usedIndices = [...previousGames];  // Копируем предыдущие индексы для исключения повторов
    previousGames = [];  // Обнуляем для нового обновления

    images.forEach((img) => {
        const randomIndex = getRandomUniqueIndex(games, usedIndices);
        const randomGame = games[randomIndex];
        const image512x512 = randomGame.Assets.find(asset => asset.includes('512x512'));
        const gameUrl = randomGame['Game URL'];

        if (image512x512) {
            const newImg = new Image();
            newImg.src = image512x512;

            newImg.onload = () => {
                img.src = image512x512;
                img.dataset.gameUrl = gameUrl;
            };

            newImg.onerror = () => {
                img.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wcAAwAB/0GtWfgAAAAASUVORK5CYII=";
            };
        }

        previousGames.push(randomIndex);  // Сохраняем новый индекс для отслеживания повторов
    });
}

// Функция для открытия игры в iframe
function openGameInIframe(gameUrl) {
    const gameSection = document.querySelector('.game-section');
    
    // Очищаем game-section и заменяем его на game-player
    gameSection.innerHTML = `
        <div class="game-player">
            <iframe src="${gameUrl}" frameborder="0" width="100%" height="100%"></iframe>
        </div>
    `;

    // Применяем стили для растягивания iframe на всю ширину и высоту блока game-section
    gameSection.style.display = 'block';
    gameSection.style.height = '100%';
}

// Возвращаемся в состояние с иконками при обновлении в режиме game-player
function exitGamePlayer() {
    const gameSection = document.querySelector('.game-section');
    gameSection.innerHTML = '';  // Очищаем текущее содержимое
    gameSection.style.display = '';  // Возвращаем отображение иконок
    gameSection.style.height = '';  // Сбрасываем высоту

    // Заполняем новый набор иконок из предварительно загруженных данных
    preloadedImages.forEach((preloaded, index) => {
        const gameIcon = document.createElement('div');
        gameIcon.className = 'game-icon';
        const img = document.createElement('img');
        img.src = preloaded.img.src;
        img.dataset.gameUrl = preloaded.gameUrl;

        gameIcon.appendChild(img);
        gameSection.appendChild(gameIcon);

        img.addEventListener('click', () => {
            openGameInIframe(preloaded.gameUrl);
        });
    });
}

// Добавляем событие на кнопку обновления
function addRefreshButtonListener() {
    const refreshButton = document.getElementById('refresh-btn');

    refreshButton.addEventListener('click', () => {
        // Применяем анимацию к кнопке обновления
        refreshButton.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            refreshButton.style.transform = 'rotate(0deg)';
        }, 300);

        // Проверяем, находимся ли мы в состоянии game-player
        const gamePlayer = document.querySelector('.game-player');
        if (gamePlayer) {
            exitGamePlayer();  // Возвращаемся в состояние с иконками
        } else {
            updateGameIcons();  // Обновляем иконки в game-section
        }
    });
}

// Запускаем подгрузку при загрузке страницы
window.onload = async () => {
    await fetchWizardData();
    replaceImages();
    observeImages();
    addRefreshButtonListener();  // Добавляем обработку клика по кнопке обновления
};
