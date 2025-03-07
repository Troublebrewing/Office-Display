import asyncio
import threading
import customtkinter as ctk

class AsyncApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Async CustomTkinter App")
        self.geometry("300x200")
        
        self.label = ctk.CTkLabel(self, text="Click the button")
        self.label.pack(pady=20)
        
        self.button = ctk.CTkButton(self, text="Run Async Task", command=self.start_async_task)
        self.button.pack(pady=20)
        
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.run_event_loop, daemon=True).start()
    
    def run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    async def async_task(self):
        await asyncio.sleep(2)  # Simulate a long-running async task
        return "Task Completed!"
    
    def start_async_task(self):
        asyncio.run_coroutine_threadsafe(self.handle_async_task(), self.loop)
    
    async def handle_async_task(self):
        self.label.configure(text="Running...")
        result = await self.async_task()
        self.label.configure(text=result)

if __name__ == "__main__":
    app = AsyncApp()
    app.mainloop()
