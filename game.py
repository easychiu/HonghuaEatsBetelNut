import tkinter as tk
from tkinter import messagebox


class HonghuaGame:
    PUZZLE_SOLUTION = "314"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("紅花吃檳榔：圖書館夜談")
        self.root.geometry("760x520")
        self.root.minsize(680, 460)

        self.inventory: set[str] = set()
        self.clues: dict[str, int] = {}
        self.code_attempts_left = 3

        self.title_label = tk.Label(
            root,
            text="紅花吃檳榔：劇情 + 解謎 Demo",
            font=("Arial", 18, "bold"),
            pady=10,
        )
        self.title_label.pack()

        self.status_var = tk.StringVar(value="狀態：尚未取得道具")
        self.status_label = tk.Label(root, textvariable=self.status_var, anchor="w", padx=10)
        self.status_label.pack(fill="x")

        self.story_text = tk.Text(root, wrap="word", height=14, font=("Arial", 13))
        self.story_text.pack(fill="both", expand=True, padx=10, pady=8)
        self.story_text.configure(state="disabled")

        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(fill="x", padx=10, pady=8)

        self.show_intro()

    def set_story(self, text: str) -> None:
        self.story_text.configure(state="normal")
        self.story_text.delete("1.0", "end")
        self.story_text.insert("1.0", text)
        self.story_text.configure(state="disabled")

    def clear_buttons(self) -> None:
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

    def set_options(self, options: list[tuple[str, callable]]) -> None:
        self.clear_buttons()
        for label, callback in options:
            btn = tk.Button(self.buttons_frame, text=label, command=callback, padx=8, pady=6)
            btn.pack(side="left", padx=5, pady=2)

    def refresh_status(self) -> None:
        item_text = self._format_inventory()
        clue_text = self._format_clues()
        self.status_var.set(f"狀態：道具[{item_text}]；線索[{clue_text}]；密碼剩餘嘗試 {self.code_attempts_left} 次")

    def _format_inventory(self) -> str:
        return "、".join(sorted(self.inventory)) if self.inventory else "無"

    def _format_clues(self) -> str:
        return " | ".join(f"{k}:{v}" for k, v in sorted(self.clues.items())) if self.clues else "尚未蒐集"

    def show_intro(self) -> None:
        self.inventory.clear()
        self.clues.clear()
        self.code_attempts_left = 3
        self.refresh_status()
        self.set_story(
            "深夜的圖書館只剩你與『紅花』。\n"
            "她低聲說：『若你找不到答案，我就要吃檳榔直到天亮。』\n\n"
            "你知道必須先蒐集線索，再決定如何面對她。"
        )
        self.set_options([
            ("開始調查", self.scene_hall),
            ("直接安撫紅花", self.scene_confront),
        ])

    def scene_hall(self) -> None:
        self.refresh_status()
        self.set_story(
            "你走到閱讀桌前，看見三樣物件：古書、羽毛筆、檳榔盒。\n"
            "它們似乎藏著同一組密碼。"
        )
        self.set_options([
            ("查看古書", self.inspect_book),
            ("查看羽毛筆", self.inspect_feather),
            ("查看檳榔盒", self.inspect_box),
            ("嘗試解鎖盒子", self.try_unlock),
            ("回去面對紅花", self.scene_confront),
        ])

    def inspect_book(self) -> None:
        self.clues["古書"] = 3
        self.refresh_status()
        self.set_story(
            "古書邊角有註記：『答案從圓周率起始。』\n"
            "你判斷第一碼是 3。"
        )
        self.set_options([
            ("繼續調查", self.scene_hall),
            ("回去面對紅花", self.scene_confront),
        ])

    def inspect_feather(self) -> None:
        self.clues["羽毛筆"] = 1
        self.refresh_status()
        self.set_story(
            "羽毛筆下壓著紙條：『一筆定心。』\n"
            "你判斷第二碼是 1。"
        )
        self.set_options([
            ("繼續調查", self.scene_hall),
            ("回去面對紅花", self.scene_confront),
        ])

    def inspect_box(self) -> None:
        self.clues["檳榔盒"] = 4
        self.refresh_status()
        self.set_story(
            "檳榔盒底部刻著『四季花開』。\n"
            "你判斷第三碼是 4。"
        )
        self.set_options([
            ("繼續調查", self.scene_hall),
            ("回去面對紅花", self.scene_confront),
        ])

    def try_unlock(self) -> None:
        if len(self.clues) < 3:
            messagebox.showinfo("線索不足", "你還沒蒐集完整線索。")
            self.scene_hall()
            return

        self._create_unlock_dialog()

    def _create_unlock_dialog(self) -> None:

        dialog = tk.Toplevel(self.root)
        dialog.title("輸入三位密碼")
        dialog.geometry("320x150")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="請輸入三位數密碼：").pack(pady=8)
        entry = tk.Entry(dialog, justify="center", font=("Arial", 14))
        entry.pack(pady=4)
        entry.focus_set()

        def submit() -> None:
            code = entry.get().strip()
            if code == self.PUZZLE_SOLUTION:
                self.inventory.add("安魂符")
                self.refresh_status()
                messagebox.showinfo("解鎖成功", "你取得了『安魂符』。")
                dialog.destroy()
                self.scene_hall()
            else:
                self.code_attempts_left -= 1
                self.refresh_status()
                if self.code_attempts_left <= 0:
                    dialog.destroy()
                    self.ending_bad("你連續輸錯密碼，檳榔盒噴出紅霧，理智瞬間崩潰。")
                else:
                    messagebox.showwarning("解鎖失敗", f"密碼錯誤，還剩 {self.code_attempts_left} 次。")

        tk.Button(dialog, text="確認", command=submit).pack(pady=10)
        dialog.bind("<Return>", lambda event: submit())

    def scene_confront(self) -> None:
        self.refresh_status()
        if "安魂符" in self.inventory:
            self.ending_true()
            return

        if len(self.clues) >= 2:
            self.ending_normal()
            return

        self.ending_bad("你準備不足就上前，紅花情緒失控，夜晚陷入危機。")

    def ending_true(self) -> None:
        self.set_story(
            "你舉起安魂符，低聲念出古書上的句子。\n"
            "紅花慢慢平靜，放下檳榔盒。\n\n"
            "【真結局】你成功化解了圖書館的異變。"
        )
        self.set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_normal(self) -> None:
        self.set_story(
            "你用已知線索穩住局面，紅花暫時停止失控。\n"
            "雖未找到完整解法，但你撐過了今晚。\n\n"
            "【普通結局】危機延後，謎團仍在。"
        )
        self.set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_bad(self, reason: str) -> None:
        self.set_story(f"{reason}\n\n【壞結局】你失去了主導權。")
        self.set_options([
            ("重新開始", self.show_intro),
            ("離開", self.root.destroy),
        ])


def main() -> None:
    root = tk.Tk()
    HonghuaGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
