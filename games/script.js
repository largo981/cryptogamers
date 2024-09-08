let previousGames = [];  // Для хранения индексов предыдущего обновления
let games;  // Храним данные об играх вне функции для повторного использования
let preloadedImages = [];  // Храним предварительно загруженные изображения
const emptyImage = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wcAAwAB/0GtWfgAAAAASUVORK5CYII=";  // Пустая картинка

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

// Функция для отображения экрана загрузки
function showLoader() {
    const loader = document.getElementById('loader');
    loader.style.display = 'flex';
}

// Функция для скрытия экрана загрузки
function hideLoader() {
    const loader = document.getElementById('loader');
    loader.style.transition = 'opacity 0.5s ease-out';
    loader.style.opacity = '0';
    setTimeout(() => {
        loader.style.display = 'none';
        document.body.classList.add('loaded');
    }, 500);
}

// Функция для замены изображений на случайные картинки и добавления кликабельности
async function replaceImages() {
    const images = document.querySelectorAll('.game-section .game-icon img');
    const usedIndices = [];  // Массив для хранения уже использованных индексов

    images.forEach((img, index) => {
        // Устанавливаем сразу пустую картинку
        img.src = emptyImage;

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
                img.src = emptyImage;
            };
        }

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

    const observer = new IntersectionObserver((entries, observer) => {
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

// Функция для открытия игры в iframe
function openGameInIframe(gameUrl) {
    const gameSection = document.querySelector('.game-section');
    
    // Очищаем game-section и заменяем его на game-player
    gameSection.innerHTML = `
        <div class="game-player">
            <iframe src="${gameUrl}" frameborder="0" width="100%" height="100%"></iframe>
        </div>
    `;

    gameSection.style.display = 'block';
    gameSection.style.height = '100%';
}

// Возвращаемся в состояние с иконками при обновлении в режиме game-player
function exitGamePlayer() {
    const gameSection = document.querySelector('.game-section');
    gameSection.innerHTML = '';  // Очищаем текущее содержимое
    gameSection.style.display = '';  // Возвращаем отображение иконок
    gameSection.style.height = '';  // Сбрасываем высоту

    preloadedImages.forEach((preloaded, index) => {
        const gameIcon = document.createElement('div');
        gameIcon.className = 'game-icon';
        const img = document.createElement('img');
        img.src = emptyImage;  // Показываем пустую картинку сначала
        img.dataset.gameUrl = preloaded.gameUrl;

        gameIcon.appendChild(img);
        gameSection.appendChild(gameIcon);

        // Подгружаем изображение при полной загрузке
        preloaded.img.onload = () => {
            img.src = preloaded.img.src;
        };

        img.addEventListener('click', () => {
            openGameInIframe(preloaded.gameUrl);
        });
    });

    preloadNewIcons();  // Подгружаем следующий набор после выхода из game-player
}

// Добавляем событие на кнопку обновления
function addRefreshButtonListener() {
    const refreshButton = document.getElementById('refresh-btn');

    refreshButton.addEventListener('click', () => {
        refreshButton.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            refreshButton.style.transform = 'rotate(0deg)';
        }, 300);

        const gamePlayer = document.querySelector('.game-player');
        if (gamePlayer) {
            exitGamePlayer();
        } else {
            updateGameIcons();
        }
    });
}

// Функция для обновления иконок при клике на refresh
function updateGameIcons() {
    const images = document.querySelectorAll('.game-section .game-icon img');
    
    const usedIndices = [...previousGames];  // Копируем предыдущие индексы для исключения повторов
    previousGames = [];  // Обнуляем для нового обновления

    images.forEach((img, index) => {
        img.src = emptyImage;  // Показываем сразу пустую картинку
        const preloaded = preloadedImages[index];
        if (preloaded) {
            const newImg = new Image();
            newImg.src = preloaded.img.src;

            newImg.onload = () => {
                img.src = preloaded.img.src;
                img.dataset.gameUrl = preloaded.gameUrl;
            };

            newImg.onerror = () => {
                img.src = emptyImage;  // Возвращаемся к пустой картинке, если ошибка
            };

            previousGames.push(preloaded);
        }
    });

    preloadNewIcons();  // Загружаем следующий набор иконок для быстрого обновления
}

// Запускаем подгрузку при загрузке страницы
window.onload = async () => {
    showLoader();  // Показываем лоадер
    await fetchWizardData();
    replaceImages();
    observeImages();
    addRefreshButtonListener();  // Добавляем обработку клика по кнопке обновления
    hideLoader();  // Убираем лоадер после загрузки данных
};
