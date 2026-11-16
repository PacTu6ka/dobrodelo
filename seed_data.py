from datetime import date, datetime, timedelta
from app import create_app
from app.models import db, User, Organization, Project, Shift, Application

app = create_app()

def seed():
    with app.app_context():
        # Очистка таблиц перед сидом
        db.drop_all()
        db.create_all()

        print("Creating users...")
        # 1. Администратор / Модератор
        admin = User(
            email='admin@dobrodelo.ru',
            full_name='Администратор Модерации',
            role='admin',
            city='Москва',
            birth_date=date(1990, 1, 1)
        )
        admin.set_password('admin123')

        # 2. Координатор НКО (Елена из истории в п. 3.1)
        coordinator = User(
            email='elena@priut.ru',
            full_name='Елена Васильева (Координатор приюта)',
            role='coordinator',
            city='Москва',
            phone='+7 (916) 123-45-67',
            birth_date=date(1986, 5, 12)
        )
        coordinator.set_password('elena123')

        # 3. Волонтёр Мария (20 лет, студентка, п. 3.1)
        maria = User(
            email='maria@student.ru',
            full_name='Мария Смирнова',
            role='volunteer',
            city='Москва',
            phone='+7 (925) 987-65-43',
            birth_date=date(2004, 3, 15), # 20+ лет
            skills='Фотосъемка, работа с животными',
            interests='Приюты, экология'
        )
        maria.set_password('maria123')

        # 4. Волонтёр Алексей (16 лет, школьник, п. 3.1)
        alexey = User(
            email='alexey@school.ru',
            full_name='Алексей Кузнецов',
            role='volunteer',
            city='Москва',
            phone='+7 (903) 555-44-33',
            birth_date=date(2008, 9, 20), # ~16 лет (несовершеннолетний)
            skills='Базовые компьютерные навыки',
            interests='Экология, парки'
        )
        alexey.set_password('alexey123')

        db.session.add_all([admin, coordinator, maria, alexey])
        db.session.commit()

        print("Creating organizations...")
        # Организация 1 (Верифицирована)
        org1 = Organization(
            name='Приют для бездомных животных «Верный друг»',
            description='Региональный приют: заботимся о 120 собаках и 80 кошках. Организуем еженедельные субботние смены для волонтёров.',
            city='Москва',
            contact_email='info@priut-vd.ru',
            contact_phone='+7 (495) 777-88-99',
            is_verified=True,
            owner_id=coordinator.id
        )

        # Организация 2 (На проверке модератором)
        org2 = Organization(
            name='Экологическое движение «Зелёный патруль»',
            description='Городская инициатива по очистке прибрежных зон и посадке деревьев.',
            city='Москва',
            contact_email='eco@greenpatrol.ru',
            contact_phone='+7 (495) 333-22-11',
            is_verified=False, # Ожидает верификации (FR-37)
            owner_id=coordinator.id
        )

        db.session.add_all([org1, org2])
        db.session.commit()

        print("Creating projects and shifts...")
        today = date.today()

        # Проект 1: Субботний приют (из истории сценария 3.2)
        proj1 = Project(
            organization_id=org1.id,
            title='Выгул, социализация собак и помощь приюту «Верный друг»',
            description='Приглашаем волонтёров помочь в субботней смене! Программа: прогулки с собаками на поводке в прилегающей лесопарковой зоне, расчёсывание, помощь в уборке вольеров. Опыт не требуется, инструктаж на месте.',
            category='Животные',
            city='Москва',
            address='ул. Лесная, д. 45, корп. 2 (Приют «Верный друг»)',
            status='open'
        )
        db.session.add(proj1)
        db.session.commit()

        # Смены для проекта 1
        shift1 = Shift(
            project_id=proj1.id,
            date=today + timedelta(days=2),
            start_time='11:00',
            end_time='15:00',
            location='Главные ворота приюта',
            max_volunteers=15,
            hours=4.0,
            min_age=14,
            parent_consent_required=True
        )

        shift2 = Shift(
            project_id=proj1.id,
            date=today + timedelta(days=9),
            start_time='11:00',
            end_time='15:00',
            location='Главные ворота приюта',
            max_volunteers=20,
            hours=4.0,
            min_age=14,
            parent_consent_required=True
        )

        # Прошедшая смена для истории часов Марии
        shift_past = Shift(
            project_id=proj1.id,
            date=today - timedelta(days=7),
            start_time='10:00',
            end_time='14:00',
            location='Главные ворота приюта',
            max_volunteers=10,
            hours=4.0,
            min_age=14,
            parent_consent_required=True
        )

        db.session.add_all([shift1, shift2, shift_past])
        db.session.commit()

        # Проект 2: Раздельный сбор отходов
        proj2 = Project(
            organization_id=org1.id,
            title='Акция по раздельному сбору вторсырья «ЭкоТочка»',
            description='Помощь в приёме макулатуры, пластика и стекла от жителей микрорайона. Информирование горожан о правилах сортировки отходов.',
            category='Экология',
            city='Москва',
            address='ПКиО Сокольники, центральная аллея',
            status='open'
        )
        db.session.add(proj2)
        db.session.commit()

        shift3 = Shift(
            project_id=proj2.id,
            date=today + timedelta(days=5),
            start_time='12:00',
            end_time='16:00',
            location='Шатер ЭкоТочка возле центрального входа',
            max_volunteers=8,
            hours=4.0,
            min_age=14,
            parent_consent_required=True
        )
        db.session.add(shift3)
        db.session.commit()

        print("Creating sample applications and hours...")
        # 1. Мария уже отработала прошлую смену (явка подтверждена, часы начислены)
        app_past = Application(
            shift_id=shift_past.id,
            volunteer_id=maria.id,
            status='attended',
            parent_consent_given=False,
            hours_awarded=4.0,
            applied_at=datetime.utcnow() - timedelta(days=8)
        )

        # 2. Мария записалась на ближайшую смену (одобрено)
        app_active = Application(
            shift_id=shift1.id,
            volunteer_id=maria.id,
            status='approved',
            parent_consent_given=False,
            applied_at=datetime.utcnow() - timedelta(days=1)
        )

        # 3. Алексей (16 лет) подал заявку с подтверждением согласия родителей (pending)
        app_minor = Application(
            shift_id=shift1.id,
            volunteer_id=alexey.id,
            status='pending',
            parent_consent_given=True, # Согласие 152-ФЗ отмечено
            applied_at=datetime.utcnow()
        )

        db.session.add_all([app_past, app_active, app_minor])
        db.session.commit()

        print("=== Database successfully populated with realistic demo data! ===")
        print("Тестовые аккаунты:")
        print("1. Волонтёр: maria@student.ru / maria123 (20 лет, 4 часа начислено)")
        print("2. Волонтёр-школьник: alexey@school.ru / alexey123 (16 лет, согласие родителей)")
        print("3. Координатор НКО: elena@priut.ru / elena123 (Приют «Верный друг»)")
        print("4. Администратор / Модератор: admin@dobrodelo.ru / admin123")

if __name__ == '__main__':
    seed()
