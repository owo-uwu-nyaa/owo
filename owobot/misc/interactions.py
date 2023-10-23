from discord import app_commands
from discord.ext import commands

class ContextMenuCog(commands.Cog):
    '''
    Cog type for ContextMenu. Extends `commands.Cog`.
    If you want cogs to be able to implement ContextMenus, 
    simply implement this Cog.

    Annotate the ContextMenu function with @context_menu_command.
    Do not include other discord.py command annotations (checks, etc. are okay).

    See context_menu_command for more information.
    '''
    def __init__(self) -> None:
        super().__init__()
        self.context_menus = []
        self.methods = [getattr(self, method) for method in dir(self) if getattr(getattr(self, method), "_context_menu", None)] 
        
        for method in self.methods:
            n = getattr(method, "_display_name", method.__name__)
            
            ctx_menu = app_commands.ContextMenu(
                name=n,
                callback=method,
            )
            self.bot.tree.add_command(ctx_menu)
            self.context_menus.append(ctx_menu)

    async def cog_unload(self) -> None:
        for menu in self.context_menus:
            self.bot.tree.remove_command(menu.name, type=menu.type)

def context_menu_command(name=None):
    '''
    Decorator for ContextMenu commands.
    This does not act like a wrapper, it basically allows us
    to run code immediately after the function f is defined.
    
    Keep in mind any prints/logging in here will NOT show up
    in the console (due to how discord.py loads commands).
    
    Parameters:
        name: String? (defaults to f.__name__)

    Usage:
        @context_menu_command(name="owoify")
        async def owoify_message():
            ...
    '''

    def decorator(f):
        setattr(f, "_context_menu", True)
        setattr(f, "_display_name", name)
        return f
    return decorator
