from datetime import datetime, timedelta

# 1. Write a Python program to subtract five days from current date.
today = datetime.now()
five_days_ago = today - timedelta(days=5)
print("Five days ago: ", five_days_ago)
print()

# 2. Write a Python program to print yesterday, today, tomorrow.
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)
print("Yesterday: ", yesterday)
print("Today: ", today)
print("Tomorrow: ", tomorrow)
print()

# 3. Write a Python program to drop microseconds from datetime.
drop = today.replace(microsecond=0)
print("Without microseconds: ", drop)
print()

# 4. Write a Python program to calculate two date difference in seconds.
n = int(input("Enter number: "))
past_date = today - timedelta(days=n)

diff = today - past_date
diff_in_seconds = diff.total_seconds()
print(f"The difference: {diff_in_seconds}")
