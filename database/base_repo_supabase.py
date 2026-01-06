from supabase import create_client
import streamlit as st


class BaseRepoSupabase:
    def __init__(self, table_name: str, id_field: str = "id"):
        self.table = table_name
        self.id_field = id_field

        self.client = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"]
        )

    # =============================
    # READ
    # =============================
    def get_all(self, order_by: str | None = None, desc: bool = False):
        query = self.client.table(self.table).select("*")

        if order_by:
            query = query.order(order_by, desc=desc)

        return query.execute().data

    def get_by_id(self, record_id):
        return (
            self.client
            .table(self.table)
            .select("*")
            .eq(self.id_field, record_id)
            .single()
            .execute()
            .data
        )

    def get_by_field(self, field: str, value):
        return (
            self.client
            .table(self.table)
            .select("*")
            .eq(field, value)
            .execute()
            .data
        )

    # =============================
    # CREATE
    # =============================
    def insert(self, record: dict):
        return (
            self.client
            .table(self.table)
            .insert(record)
            .execute()
            .data
        )

    def insert_and_return_id(self, record: dict):
        result = (
            self.client
            .table(self.table)
            .insert(record)
            .execute()
            .data
        )

        if not result:
            raise RuntimeError("No se pudo insertar el registro")

        return result[0][self.id_field]
    # =============================
    # UPDATE
    # =============================
    def update(self, record_id, updates: dict):
        return (
            self.client
            .table(self.table)
            .update(updates)
            .eq(self.id_field, record_id)
            .execute()
            .data
        )

    # =============================
    # DELETE
    # =============================
    def delete(self, record_id):
        return (
            self.client
            .table(self.table)
            .delete()
            .eq(self.id_field, record_id)
            .execute()
            .data
        )
    # =============================
    # DELETE BY FIELD
    # =============================
    def delete_by_field(self, field, value):
        """
        Elimina registros donde field == value
        """
        return (
            self.client
            .table(self.table)
            .delete()
            .eq(field, value)
            .execute()
            .data
        )



