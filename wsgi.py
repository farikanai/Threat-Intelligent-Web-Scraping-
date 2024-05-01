import os

def main():
	os.system("gunicorn -w 2 -b 138.68.70.178:8001 'app:app'")

if __name__ == "__main__":
	main()