import {defaults} from 'lodash';

const cases = [2, 0, 1, 1, 1, 2];
//функция выбора склонения слов на основе числительного
//Пример вывода: 2 мясяца.
export type params = {
    value: number, 
    words: [string, string, string], 
    showNumber?: boolean;
}

export const declinationOfNumber = (params: params) => {
    const def: Partial<params> = {
        showNumber: true
    };
    const merged = defaults(params, def);
    const {value, words, showNumber} = merged;

    const isThirdDeclination = value % 100 > 4 && value % 100 < 20; //если значение больше 4 но меньше 20, либо больше 104 но меньше 120 и т.д (5, 105 месяцев)
    const selectWord = cases[(value % 10 < 5) ? value % 10 : 5]; //2-4 (21-24) второе слово массива, 1 (21) - первое, 0 (20) - третье
    if (showNumber) return `${value} ${words[(isThirdDeclination) ? 2 : selectWord]}`;
    return `${words[(isThirdDeclination) ? 2 : selectWord]}`;
};