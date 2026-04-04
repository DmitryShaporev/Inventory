import sqlite3
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Миграция данных для выделения НДС в старых документах'

    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']

        self.stdout.write(f"Подключение к БД: {db_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Шаг 1: Принудительно установить ставку НДС по дате документа
            self.stdout.write("Шаг 1: Устанавливаем ставку НДС по дате документа...")

            # Сначала обнуляем все ставки, чтобы точно установить
            cursor.execute("""
                UPDATE detail 
                SET vat_rate = 0
            """)
            self.stdout.write(f"  - Обнулены все ставки: {cursor.rowcount} записей")

            # Устанавливаем 20% для документов до 2026
            cursor.execute("""
                UPDATE detail 
                SET vat_rate = 20.00
                WHERE id_doc IN (SELECT id FROM doc WHERE datadoc <= '2025-12-31')
            """)
            self.stdout.write(f"  - Установлено 20% для документов до 2026: {cursor.rowcount} записей")

            # Устанавливаем 22% для документов с 2026
            cursor.execute("""
                UPDATE detail 
                SET vat_rate = 22.00
                WHERE id_doc IN (SELECT id FROM doc WHERE datadoc >= '2026-01-01')
            """)
            self.stdout.write(f"  - Установлено 22% для документов с 2026: {cursor.rowcount} записей")

            # Шаг 2: Переносим cost в total_with_vat (если total_with_vat пустой или 0)
            self.stdout.write("Шаг 2: Переносим cost в total_with_vat...")

            cursor.execute("""
                UPDATE detail 
                SET total_with_vat = cost
                WHERE total_with_vat IS NULL OR total_with_vat = 0
            """)
            self.stdout.write(f"  - Обновлено total_with_vat: {cursor.rowcount} записей")

            # Шаг 3: Вычисляем НДС и новую стоимость без НДС
            self.stdout.write("Шаг 3: Вычисляем НДС и стоимость без НДС...")

            # Для записей с НДС (vat_rate > 0)
            cursor.execute("""
                UPDATE detail 
                SET 
                    vat_amount = ROUND(total_with_vat - (total_with_vat / (1 + vat_rate/100)), 2),
                    cost = ROUND(total_with_vat / (1 + vat_rate/100), 2)
                WHERE vat_rate IS NOT NULL 
                  AND vat_rate != 0
                  AND total_with_vat IS NOT NULL
                  AND total_with_vat != 0
            """)
            self.stdout.write(f"  - Рассчитано НДС для: {cursor.rowcount} записей")

            # Для записей без НДС (vat_rate = 0)
            cursor.execute("""
                UPDATE detail 
                SET 
                    vat_amount = 0,
                    cost = total_with_vat
                WHERE (vat_rate IS NULL OR vat_rate = 0)
                  AND total_with_vat IS NOT NULL
            """)
            self.stdout.write(f"  - Обнулено НДС для: {cursor.rowcount} записей")

            # Шаг 4: Проверка результата
            self.stdout.write("Шаг 4: Проверка результата...")

            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN vat_rate = 20 THEN 1 ELSE 0 END) as vat_20,
                    SUM(CASE WHEN vat_rate = 22 THEN 1 ELSE 0 END) as vat_22,
                    SUM(CASE WHEN vat_rate = 0 THEN 1 ELSE 0 END) as vat_0
                FROM detail
            """)
            result = cursor.fetchone()
            self.stdout.write(f"  - Всего записей: {result[0]}")
            self.stdout.write(f"  - НДС 20%: {result[1]}")
            self.stdout.write(f"  - НДС 22%: {result[2]}")
            self.stdout.write(f"  - Без НДС: {result[3]}")

            # Проверка цен (цены не должны измениться)
            self.stdout.write("Шаг 5: Проверка цен (цены не должны измениться)...")

            cursor.execute("""
                SELECT COUNT(*) 
                FROM detail 
                WHERE price IS NULL OR price = 0
            """)
            zero_prices = cursor.fetchone()[0]
            self.stdout.write(f"  - Записей с нулевой ценой: {zero_prices}")

            # Проверка совпадения итогов документов
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT d.id
                    FROM doc d
                    LEFT JOIN detail dt ON d.id = dt.id_doc
                    GROUP BY d.id
                    HAVING ROUND(d.total, 2) != ROUND(COALESCE(SUM(dt.total_with_vat), 0), 2)
                ) as mismatches
            """)
            mismatches = cursor.fetchone()[0]
            if mismatches > 0:
                self.stdout.write(self.style.WARNING(f"  - Внимание: у {mismatches} документов итоги не совпадают"))
            else:
                self.stdout.write("  - Все итоги документов совпадают!")

            conn.commit()
            self.stdout.write(self.style.SUCCESS("\n✅ Миграция НДС успешно завершена!"))

        except Exception as e:
            conn.rollback()
            self.stdout.write(self.style.ERROR(f"\n❌ Ошибка: {e}"))
            raise

        finally:
            conn.close()