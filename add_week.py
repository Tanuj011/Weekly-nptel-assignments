"""
Script to easily add new weeks to the NPTEL database
Usage: python add_week.py
"""

from app import app, db, Week, Question
import json

def add_week():
    with app.app_context():
        print("\n=== Add New Week to NPTEL Database ===\n")
        
        week_number = int(input("Week Number: "))
        title = input("Week Title: ")
        due_date = input("Due Date (e.g., 2026-03-04, 23:59 IST): ")
        status = input("Status (upcoming/active/completed) [default: upcoming]: ") or "upcoming"
        
        # Create week
        week = Week(
            week_number=week_number,
            title=title,
            due_date=due_date,
            status=status
        )
        db.session.add(week)
        db.session.commit()
        
        print(f"\n✓ Week {week_number} created successfully!")
        
        # Add questions
        num_questions = int(input("\nHow many questions for this week? "))
        
        for i in range(num_questions):
            print(f"\n--- Question {i+1} ---")
            question_text = input("Question text: ")
            
            # Options
            print("Enter options (one per line, press Enter twice when done):")
            options = []
            while True:
                option = input()
                if option == "":
                    break
                options.append(option)
            
            answer = input("Correct answer: ")
            points = int(input("Points [default: 1]: ") or "1")
            
            question = Question(
                week_id=week.id,
                question_number=i+1,
                question_text=question_text,
                options=json.dumps(options) if options else None,
                answer=answer,
                points=points
            )
            db.session.add(question)
        
        db.session.commit()
        print(f"\n✓ Added {num_questions} questions successfully!")
        print(f"\n🎉 Week {week_number} is now available in the application!")

if __name__ == "__main__":
    add_week()
