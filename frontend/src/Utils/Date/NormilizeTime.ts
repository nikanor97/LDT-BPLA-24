export const getTimeInMinute = (secounds: number) => {
    const mins = Math.floor(secounds / 60);
    const sec = Math.floor(secounds % 60);

    let minsStr = mins.toString();
    let secStr = sec.toString();

    if (mins < 10) minsStr = `0${mins}`;
    if (sec < 10) secStr = `0${sec}`;

    return `${minsStr}:${secStr}`;
}