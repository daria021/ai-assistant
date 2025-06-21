// чистый список ролей, ДОСТУПНЫЙ в рантайме для <select>, кнопок и т.п.
export const USER_ROLES = ['manager', 'admin', 'publications_manager', 'banned'] as const;

// тип, соответствующий любому элементу нашего массива
export type UserRole = typeof USER_ROLES[number];
