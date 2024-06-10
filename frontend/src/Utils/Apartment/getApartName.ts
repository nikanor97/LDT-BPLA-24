export const isApartNumber = (value: string | number | undefined) => {
    if (value === undefined) return false;
    if (typeof value === 'number') return true
    if (/^\d+$/.test(value)) return true
    else return false;
} 

export const getApartName = (value: string | number | undefined) => {
    if (value === undefined) return null;
    if (typeof value === 'number') return `Квартира №${value}`;
    if (/^\d+$/.test(value)) return `Квартира №${value}`; 
    else return value
}