let currentX = 0;
let currentY = 0;

function rotateCube() {
    // Увеличиваем угол вращения по оси Y на 90 градусов
    currentY += 1080
    currentX += 1080

    const cube = document.querySelector('.cube');
    cube.style.transform = `rotateX(${currentX}deg) rotateY(${currentY}deg)`;
}

document.querySelector('.loading-icon').addEventListener('click', () => {
    const cube = document.querySelector('.cube');
    
    // Сбрасываем класс анимации, если был
    cube.classList.remove('animate');
    
    // Запускаем анимацию через небольшой таймаут
    setTimeout(() => {
        cube.classList.add('animate');
    }, 100);
    
    // После окончания анимации убираем класс, если нужно перезапускать анимацию
    setTimeout(() => {
        cube.classList.remove('animate');
    }, 1500); // Длительность анимации 1.5 секунды
});