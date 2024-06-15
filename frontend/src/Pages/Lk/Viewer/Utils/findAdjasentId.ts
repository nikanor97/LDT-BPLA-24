import { Video, Photo } from "@root/Types";

const findAdjacentId = (
    idArray: (Video.Item['content_id'] | Photo.Item['content_id'])[],
    openId:Video.Item['content_id'] | Photo.Item['content_id'],
    direction: "previous" | "next"): string | null => {
    const currentIndex = idArray.indexOf(openId);
    if (currentIndex === -1) {
        return null; // Возвращаем null, если переданный id не найден в массиве
    }

    if (direction === 'previous' && currentIndex > 0) {
        return idArray[currentIndex - 1]; // Возвращаем предыдущий id, если он существует
    } else if (direction === 'next' && currentIndex < idArray.length - 1) {
        return idArray[currentIndex + 1]; // Возвращаем следующий id, если он существует
    } else {
        return null; // Возвращаем null, если не удалось найти предыдущий или следующий id
    }
};

export default findAdjacentId;