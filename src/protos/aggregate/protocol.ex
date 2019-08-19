defmodule CoreTx.Aggregate do
  defmodule Rpc do
    import ForgeSdk.Tx.Builder, only: [tx: 1]
    tx :aggregate
  end

  defmodule VerifyTime do

    use ForgeAbi.Unit
    use ForgePipe.Builder

    @seconds_per_hour 60 * 60
    @thirty_seconds 30

    def init(opts), do: opts

    def call(%{context: context, itx: itx} = info, _opts) do
      itx_seconds = itx.time.seconds
      block_seconds = context.block_time.seconds
      case (itx_seconds < block_seconds or itx_seconds - block_seconds <= @thirty_seconds) and block_seconds - itx_seconds <= @seconds_per_hour do
        true -> info
        _ -> put_status(info, :invalid_time)
      end 
    end
  end

  defmodule UpdateTx do
    @moduledoc """
    create asset pipe
    """
    use ForgeAbi.Unit
    use ForgePipe.Builder

    require Logger

    def init(opts), do: opts

    def call(info, _opts) do
      update_one_state(info, [:priv, :operator_state])
      update_one_state(info, [:priv, :manufacturer_state])
      update_one_state(info, [:priv, :supplier_state])
      update_one_state(info, [:priv, :location_state])

      put_status(info, :ok)
    end

    defp update_one_state(%{itx: itx, db_handler: handler, context: context} = info, path) do
      state = get(info, path)
      new_state = CoreState.Account.update(state, %{balance: state.balance + itx.value}, context)
      :ok = handler.put!(new_state.address, new_state)
      :ok
    end 
  end
end
